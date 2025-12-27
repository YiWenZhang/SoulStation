from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import desc
from ..extensions import db
from ..models import AssessmentReport, AIConsultation, AssessmentSession
from ..utils.prompt_builder import PromptBuilder
from ..utils.ai_client import AIClient
from ..services.consultation_service import ConsultationService
from flask import Blueprint, request, jsonify, current_app, Response, stream_with_context
from ..services.consultation_service import ConsultationService
import json

# 创建独立的 Blueprint
# 注意：url_prefix 设置为 '/api/consultation'
# 这样下面的路由只需要写 '/start', '/chat'，访问时就是 '/api/consultation/start'
ai_bp = Blueprint('ai_api', __name__, url_prefix='/api/consultation')

# 初始化工具类
prompt_builder = PromptBuilder()
ai_client = AIClient()


# ==========================================
# 【新增】获取用于问诊的历史报告列表
# GET /api/consultation/history?uid=123
# ==========================================
@ai_bp.route('/history', methods=['GET'])
def get_consultation_history():
    uid = request.args.get('uid')
    if not uid:
        return jsonify({'code': 400, 'msg': 'Missing uid', 'data': []}), 400

    try:
        # 1. 查询该用户所有已完成的测评会话 (按时间倒序)
        sessions = AssessmentSession.query.filter_by(
            user_id=uid,
            status='completed'
        ).order_by(desc(AssessmentSession.updated_at)).all()

        result_list = []

        for session in sessions:
            report = session.report
            if not report:
                continue

            # 2. 查询该报告最近一次 AI 问诊记录 (用于显示时间)
            last_consultation = AIConsultation.query.filter_by(
                report_id=report.id
            ).order_by(desc(AIConsultation.updated_at)).first()

            last_time_str = None
            if last_consultation:
                last_time_str = last_consultation.updated_at.strftime('%Y-%m-%d %H:%M')

            # 3. 构造前端需要的字段
            result_list.append({
                "id": report.id,  # 报告ID
                "date": report.generated_at.strftime('%Y-%m-%d'),  # 测评日期
                "mode": session.mode,
                "mode_name": "AI对话测评" if session.mode == 'ai_chat' else "专业量表测评",
                "risk_level": report.risk_level,  # good/moderate/severe
                "summary": report.summary_short,  # 简短结论

                # --- AI 问诊特有字段 ---
                "consultation_count": report.consultation_count or 0,  # 已问诊次数
                "last_consultation_time": last_time_str  # 最近问诊时间 (用于显示 "上次问诊于...")
            })

        return jsonify({
            "code": 200,
            "msg": "获取成功",
            "data": result_list
        })

    except Exception as e:
        current_app.logger.error(f"Get consultation history failed: {str(e)}")
        return jsonify({'code': 500, 'msg': str(e), 'data': []}), 500

# ==========================================
# 1. 发起问诊 (POST /api/consultation/start)
# ==========================================
@ai_bp.route('/start', methods=['POST'])
def start_consultation():
    data = request.json
    report_id = data.get('report_id')

    if not report_id:
        return jsonify({'error': 'Missing report_id'}), 400

    # 1. 【新增逻辑】查找是否存在该报告的“进行中”问诊
    # 判定标准：diagnosis_summary 为空表示 AI 还没给出最终总结，问诊仍在进行
    existing_consultation = AIConsultation.query.filter_by(
        report_id=report_id,
        diagnosis_summary=None  # 或者根据你定义的 consultation_status == 'ongoing'
    ).order_by(AIConsultation.updated_at.desc()).first()

    if existing_consultation:
        # 如果找到了，直接返回已有的 ID 和最后一条 AI 回复（从 chat_history 提取）
        history = existing_consultation.chat_history
        last_ai_message = ""
        # 寻找历史记录中最后一条 assistant 的话作为开场回复
        for msg in reversed(history):
            if msg['role'] == 'assistant':
                last_ai_message = msg['content']
                break

        return jsonify({
            'consultation_id': existing_consultation.id,
            'sequence_number': existing_consultation.sequence_number,
            'message': last_ai_message or "欢迎回来，我们继续之前的问诊。",
            'status': 'ongoing',
            'is_resume': True  # 告知前端这是“恢复”而不是“新开启”
        })

    report = AssessmentReport.query.get(report_id)
    if not report:
        return jsonify({'error': 'Report not found'}), 404

    try:
        # 1. 计算复诊次数
        count = AIConsultation.query.filter_by(report_id=report.id).count()
        sequence_number = count + 1

        # 2. 构建 Prompt 上下文 (包含人设、知识库、历史病历)
        prev_scores = None
        if sequence_number > 1:
            prev_con = AIConsultation.query.filter_by(
                report_id=report.id,
                sequence_number=count  # 上一次的序号
            ).first()
            if prev_con:
                prev_scores = prev_con.final_scores

        initial_messages = prompt_builder.build_consultant_messages(
            report,
            sequence_number=sequence_number,
            prev_scores=prev_scores
        )
        # 3. AI 发起第一句开场白
        ai_response_text = ai_client.get_response(initial_messages)

        # 4. 存入数据库
        # 将 System Prompt 和开场白作为历史记录的起点
        chat_history = initial_messages + [
            {"role": "assistant", "content": ai_response_text}
        ]

        consultation = AIConsultation(
            report_id=report.id,
            user_id=report.session.user_id if report.session else None,  # 确保关联正确
            sequence_number=sequence_number,
            chat_history=chat_history,
            current_step=1
        )

        # 更新 Report 状态
        report.consultation_count = sequence_number
        report.consultation_status = 'ongoing'

        db.session.add(consultation)
        db.session.commit()

        return jsonify({
            'consultation_id': consultation.id,
            'sequence_number': sequence_number,
            'message': ai_response_text,
            'status': 'ongoing'
        })

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Start consultation failed: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ==========================================
# 2. 对话交互 (POST /api/consultation/chat)
# ==========================================
@ai_bp.route('/chat/stream', methods=['POST'])
def chat_consultation_stream():
    data = request.json
    consultation_id = data.get('consultation_id')
    user_content = data.get('content')

    if not consultation_id or not user_content:
        return jsonify({'error': 'Missing parameters'}), 400

    def generate():
        # 调用 Service 层获取生成器
        # Service 返回的是 (type, data) 的元组，Route 层负责将其格式化为 SSE 协议
        for event_type, payload in ConsultationService.process_chat_stream(consultation_id, user_content):
            # SSE 格式: data: <json_string>\n\n
            # 我们可以加一个 event 字段方便前端区分消息类型
            response_obj = {
                "type": event_type,  # message | finished | error | done
                "content": payload  # 具体的文本或对象
            }
            yield f"data: {json.dumps(response_obj, ensure_ascii=False)}\n\n"

    # 返回流式响应
    return Response(stream_with_context(generate()), mimetype='text/event-stream')




# ==========================================
# 3. 手动结束 (POST /api/consultation/finish)
# ==========================================
@ai_bp.route('/finish', methods=['POST'])
def finish_consultation():
    """用户点击按钮强制结束"""
    data = request.json
    consultation_id = data.get('consultation_id')

    if not consultation_id:
        return jsonify({'code': 400, 'msg': '缺少问诊ID'}), 400

    consultation = AIConsultation.query.get(consultation_id)
    if not consultation:
        return jsonify({'code': 404, 'msg': '未找到问诊记录'}), 404

    # 如果已经生成过总结，说明之前已结束，直接返回
    if consultation.diagnosis_summary:
        return jsonify({
            'code': 200,
            'status': 'finished',
            'msg': '问诊之前已完成',
            'data': {
                'consultation_id': consultation.id
            }
        })

    try:
        # 1. 强制生成总结（内部会触发数据量化入库）
        # 确保传入了 consultation 对象以更新其 final_scores 等字段
        summary = _generate_diagnosis_summary(consultation.chat_history, consultation, manual=True)

        # 2. 更新状态
        consultation.diagnosis_summary = summary
        if consultation.report:
            consultation.report.consultation_status = 'completed'

        # 3. 显式提交事务，确保写入 ai_consultations 表
        db.session.commit()

        # 4. 返回统一的结束标志给前端
        return jsonify({
            'code': 200,
            'status': 'finished',
            'msg': '问诊已手动结束，正在生成报告...',
            'data': {
                'consultation_id': consultation.id,
                'report_preview': summary[:100]  # 返回预览，增加用户感知
            }
        })

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Manual finish failed: {str(e)}")
        return jsonify({'code': 500, 'msg': f"结束失败: {str(e)}"}), 500


# ==========================================
# 【新增】获取问诊详细结果 (用于报告展示和历史复用)
# GET /api/consultation/detail/<int:consultation_id>
# ==========================================
@ai_bp.route('/detail/<int:consultation_id>', methods=['GET'])
def get_consultation_detail(consultation_id):
    """
    获取 AI 问诊的完整详细结果
    包含：初始分数、AI 修正分数、分数变化幅度、MD 总结及风险等级
    """
    try:
        # 1. 查询问诊记录及其关联的原始报告
        consultation = AIConsultation.query.get(consultation_id)

        if not consultation:
            return jsonify({'code': 404, 'msg': '未找到该问诊记录'}), 404

        # 获取关联的原始报告数据
        report = consultation.report
        initial_scores = report.radar_data if report else {}

        # 如果是复诊，获取上一轮的 AI 修正分数作为前端显示的基准
        if consultation.sequence_number > 1:
            prev = AIConsultation.query.filter_by(
                report_id=consultation.report_id,
                sequence_number=consultation.sequence_number - 1
            ).first()
            if prev and prev.final_scores:
                initial_scores = prev.final_scores

        # 2. 构造响应数据
        result_data = {
            "id": consultation.id,
            "report_id": consultation.report_id,
            "sequence_number": consultation.sequence_number,

            # --- 核心内容 ---
            "diagnosis_summary": consultation.diagnosis_summary,  # MD 总结结论

            # --- 分数对比数据 ---
            "initial_scores": initial_scores,
            # AI 问诊后修正的维度分数
            "final_scores": consultation.final_scores,
            # 相比初始分数的变化幅度 (由 ConsultationService 计算)
            "score_changes": consultation.score_changes,

            # --- 风险等级对比 ---
            "initial_risk_level": report.risk_level if report else None,
            "final_risk_level": consultation.final_risk_level,  #

            # --- 状态与时间 ---
            "status": "finished" if consultation.diagnosis_summary else "ongoing",
            "updated_at": consultation.updated_at.strftime('%Y-%m-%d %H:%M'),

            # 如果前端需要重新渲染对话，可以带上历史记录
            "chat_history": consultation.chat_history
        }

        return jsonify({
            "code": 200,
            "msg": "获取成功",
            "data": result_data
        })

    except Exception as e:
        current_app.logger.error(f"Get consultation detail failed: {str(e)}")
        return jsonify({'code': 500, 'msg': f"服务器错误: {str(e)}"}), 500


# ==========================================
# 4. 内部辅助函数
# ==========================================
def _generate_diagnosis_summary(chat_history, consultation,manual=False):
    """提取对话生成病历"""
    conversation_text = ""
    for msg in chat_history:
        if msg['role'] in ['user', 'assistant']:
            role = "医生" if msg['role'] == 'assistant' else "患者"
            conversation_text += f"{role}: {msg['content']}\n"

    prompt_content = f"""
【指令】
你是专业的医疗文书记录员。请根据以下的医患对话记录，整理一份结构化的心理咨询病历（Markdown格式）。

【对话记录】
{conversation_text}

【输出要求】
1. **现状分析**：总结患者的核心症状、持续时间及诱发因素。
2. **风险评估**：明确指出是否存在自伤、自杀或社会功能受损风险。
3. **行动建议**：列出医生在对话中给出的具体建议（如行为训练、认知调整或就医指引）。
{"4. **备注**：由于患者主动中断了问诊，以上结论可能基于不完整信息。" if manual else ""}

请直接输出 Markdown 内容。

【量化评估要求】
重要：在量化评估要求部分的开头，生成四个字“以下删除”并换行，因为这一部分不显示到前端！！！！
    请根据对话内容，重新评估 SCL-90 各维度的当前分数（1.0-5.0，保留两位小数）。
    并在回复的最后，以 JSON 格式输出如下数据：
    {{
      "scores": {{ "躯体化": 1.5, "抑郁": 3.2, ... }}
    }}
"""
    messages = [
        {"role": "system", "content": "你是一名心理医生助理。"},
        {"role": "user", "content": prompt_content}
    ]
    ai_raw_response = ai_client.get_response(messages)
    ConsultationService.update_consultation_data(consultation, ai_raw_response)

    return ai_raw_response