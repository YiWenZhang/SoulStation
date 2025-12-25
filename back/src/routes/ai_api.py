from flask import Blueprint, request, jsonify, current_app
from ..extensions import db
from ..models import AssessmentReport, AIConsultation
from ..utils.prompt_builder import PromptBuilder
from ..utils.ai_client import AIClient

# 创建独立的 Blueprint
# 注意：url_prefix 设置为 '/api/consultation'
# 这样下面的路由只需要写 '/start', '/chat'，访问时就是 '/api/consultation/start'
ai_bp = Blueprint('ai_api', __name__, url_prefix='/api/consultation')

# 初始化工具类
prompt_builder = PromptBuilder()
ai_client = AIClient()


# ==========================================
# 1. 发起问诊 (POST /api/consultation/start)
# ==========================================
@ai_bp.route('/start', methods=['POST'])
def start_consultation():
    data = request.json
    report_id = data.get('report_id')

    if not report_id:
        return jsonify({'error': 'Missing report_id'}), 400

    report = AssessmentReport.query.get(report_id)
    if not report:
        return jsonify({'error': 'Report not found'}), 404

    try:
        # 1. 计算复诊次数
        count = AIConsultation.query.filter_by(report_id=report.id).count()
        sequence_number = count + 1

        # 2. 构建 Prompt 上下文 (包含人设、知识库、历史病历)
        initial_messages = prompt_builder.build_messages(report)

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
@ai_bp.route('/chat', methods=['POST'])
def chat_consultation():
    data = request.json
    consultation_id = data.get('consultation_id')
    user_content = data.get('content')

    if not consultation_id or not user_content:
        return jsonify({'error': 'Missing parameters'}), 400

    consultation = AIConsultation.query.get(consultation_id)
    if not consultation:
        return jsonify({'error': 'Consultation not found'}), 404

    if consultation.diagnosis_summary:
        return jsonify({'error': 'Consultation finished'}), 400

    try:
        # 1. 更新对话历史
        history = list(consultation.chat_history)
        history.append({"role": "user", "content": user_content})

        # 2. 调用 AI
        ai_raw_response = ai_client.get_response(history)

        # 3. 检查自动结束信号
        is_finished = "<END_DIAGNOSIS>" in ai_raw_response
        clean_response = ai_raw_response.replace("<END_DIAGNOSIS>", "").strip()

        # 4. 保存回复
        history.append({"role": "assistant", "content": clean_response})
        consultation.chat_history = history
        consultation.current_step += 1

        response_data = {
            'message': clean_response,
            'status': 'ongoing'
        }

        # 5. 如果触发结束信号，自动生成病历
        if is_finished:
            summary = _generate_diagnosis_summary(history, manual=False)
            consultation.diagnosis_summary = summary
            consultation.report.consultation_status = 'completed'

            response_data['status'] = 'finished'
            response_data['report'] = summary

        db.session.commit()
        return jsonify(response_data)

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Chat failed: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ==========================================
# 3. 手动结束 (POST /api/consultation/finish)
# ==========================================
@ai_bp.route('/finish', methods=['POST'])
def finish_consultation():
    """用户点击按钮强制结束"""
    data = request.json
    consultation_id = data.get('consultation_id')

    if not consultation_id:
        return jsonify({'error': 'Missing consultation_id'}), 400

    consultation = AIConsultation.query.get(consultation_id)
    if not consultation:
        return jsonify({'error': 'Consultation not found'}), 404

    if consultation.diagnosis_summary:
        return jsonify({
            'status': 'finished',
            'report': consultation.diagnosis_summary
        })

    try:
        # 强制总结
        summary = _generate_diagnosis_summary(consultation.chat_history, manual=True)

        consultation.diagnosis_summary = summary
        consultation.report.consultation_status = 'completed'
        db.session.commit()

        return jsonify({
            'status': 'finished',
            'message': '问诊已结束',
            'report': summary
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==========================================
# 4. 内部辅助函数
# ==========================================
def _generate_diagnosis_summary(chat_history, manual=False):
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
"""
    messages = [
        {"role": "system", "content": "你是一名心理医生助理。"},
        {"role": "user", "content": prompt_content}
    ]
    return ai_client.get_response(messages)