from ..extensions import db
from ..models import AIConsultation
from ..utils.ai_client import AIClient
from ..utils.prompt_builder import PromptBuilder
from sqlalchemy.orm.attributes import flag_modified
import json
import re


class ConsultationService:
    @staticmethod
    def parse_ai_json_scores(ai_raw_response):
        """
        从 AI 的原生回复中提取 JSON 评分数据
        """
        try:
            # 使用正则匹配回复中的 JSON 块
            match = re.search(r'\{.*\}', ai_raw_response, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception as e:
            print(f"Error parsing JSON: {e}")
            return None
        return None

    @staticmethod
    def calculate_score_changes(initial_radar_data, final_scores):
        """
        对比初始问卷和 AI 问诊的分数变化

        现在 initial_radar_data 已经是字典格式，与 final_scores 格式一致
        """
        changes = {}

        # 确保 initial_radar_data 是字典格式
        if isinstance(initial_radar_data, str):
            try:
                initial_radar_data = json.loads(initial_radar_data)
            except:
                initial_radar_data = {}
        elif not isinstance(initial_radar_data, dict):
            print(f"Warning: initial_radar_data is not a dict: {type(initial_radar_data)}")
            initial_radar_data = {}

        print(f"Debug: Initial radar data: {initial_radar_data}")
        print(f"Debug: Final scores: {final_scores}")

        # 遍历所有维度，计算变化
        all_dimensions = set(list(initial_radar_data.keys()) + list(final_scores.keys()))

        for dim in all_dimensions:
            try:
                old_score = float(initial_radar_data.get(dim, 0))
                new_score = float(final_scores.get(dim, 0))
                # 计算变化（保留两位小数）
                change = round(new_score - old_score, 2)
                changes[dim] = change
                print(f"Debug: {dim}: {old_score} -> {new_score} = {change}")
            except Exception as e:
                print(f"Error calculating change for {dim}: {e}")
                changes[dim] = 0.0

        return changes

    @staticmethod
    def update_consultation_data(consultation, ai_raw_response):
        """
        核心封装函数：解析、计算并保存结果到数据库
        """
        print(f"\n=== Debug: update_consultation_data started ===")

        # 1. 解析 AI 输出的 JSON
        data = ConsultationService.parse_ai_json_scores(ai_raw_response)
        if not data:
            print("Error: Failed to parse AI JSON response")
            return False

        print(f"Debug: Parsed AI data: {data}")

        try:
            # 2. 提取并更新数据
            final_scores = data.get("scores", {})
            if not final_scores:
                print("Warning: No 'scores' key found in AI response, using data directly")
                final_scores = data

            print(f"Debug: Final scores to save: {final_scores}")

            # 获取问卷报告的原始分数（已经是字典格式）
            # ------------------------------------------------------------------
            # 【修改开始】确定对比的基准分数 (initial_radar)
            # ------------------------------------------------------------------
            initial_radar = {}

            # 默认使用原始问卷数据 (Baseline)
            if consultation.report and consultation.report.radar_data:
                initial_radar = consultation.report.radar_data
                if isinstance(initial_radar, str):
                    try:
                        initial_radar = json.loads(initial_radar)
                    except:
                        initial_radar = {}

            # 如果是复诊 (sequence_number > 1)，尝试获取“上一次”问诊的结果作为对比基准
            if consultation.sequence_number > 1:
                try:
                    # 动态导入 AIConsultation 以避免循环导入 (如果都在 services 里可能需要，或者直接用传入的对象的类)
                    # from ..models import AIConsultation

                    # 查询上一轮问诊记录
                    # 注意：这里假设 AIConsultation 模型已经引入，或者使用 consultation.__class__
                    prev_consultation = consultation.__class__.query.filter_by(
                        report_id=consultation.report_id,
                        sequence_number=consultation.sequence_number - 1
                    ).first()

                    if prev_consultation and prev_consultation.final_scores:
                        print(f"Debug: 复诊模式，对比上一轮 (Seq: {prev_consultation.sequence_number}) 的分数")
                        prev_scores = prev_consultation.final_scores
                        # 确保格式正确
                        if isinstance(prev_scores, str):
                            prev_scores = json.loads(prev_scores)

                        # 只有当上一轮有有效分数时才覆盖
                        if prev_scores:
                            initial_radar = prev_scores
                    else:
                        print("Debug: 未找到上一轮有效分数，降级对比原始问卷")
                except Exception as e:
                    print(f"Warning: 获取上一轮问诊数据失败: {e}")
            else:
                print("Debug: 初诊模式，对比原始问卷分数")

            print(f"Debug: Comparison Base (Initial radar): {initial_radar}")
            # ------------------------------------------------------------------
            # 【修改结束】
            # ------------------------------------------------------------------



            # 保存 AI 问诊后的分数
            consultation.final_scores = final_scores

            # 计算分数变化
            consultation.score_changes = ConsultationService.calculate_score_changes(
                initial_radar,
                final_scores
            )

            print(f"Debug: Score changes: {consultation.score_changes}")

            # 3. 更新最终风险等级
            if final_scores:
                try:
                    # 找到最高分
                    scores_values = [float(v) for v in final_scores.values() if v is not None]
                    if scores_values:
                        max_score = max(scores_values)

                        # 根据业务规则设置风险等级
                        if max_score >= 3.0:
                            consultation.final_risk_level = 'severe'
                        elif max_score >= 2.0:
                            consultation.final_risk_level = 'moderate'
                        else:
                            consultation.final_risk_level = 'good'

                        print(f"Debug: Risk level: {consultation.final_risk_level} (max_score: {max_score})")
                    else:
                        consultation.final_risk_level = 'good'
                except Exception as e:
                    print(f"Error calculating risk level: {e}")
                    consultation.final_risk_level = 'good'
            else:
                consultation.final_risk_level = 'good'

            # 4. 可选：计算好转率或改善百分比
            # 这里简单计算总分变化百分比作为示例
            try:
                if initial_radar and final_scores:
                    initial_total = sum([float(v) for v in initial_radar.values()])
                    final_total = sum([float(v) for v in final_scores.values()])
                    if initial_total > 0:
                        improvement_rate = round((initial_total - final_total) / initial_total * 100, 1)
                        consultation.improvement_rate = improvement_rate
                        print(f"Debug: Improvement rate: {improvement_rate}%")
            except Exception as e:
                print(f"Error calculating improvement rate: {e}")

            # 5. 【关键】显式通知 SQLAlchemy JSON 字段已修改
            flag_modified(consultation, "final_scores")
            flag_modified(consultation, "score_changes")
            flag_modified(consultation, "final_risk_level")
            flag_modified(consultation, "improvement_rate")

            # 6. 【关键】提交事务，写入数据库
            db.session.commit()
            print("=== Debug: Successfully updated consultation data ===")

            # 验证数据已保存
            print(f"Debug: Consultation saved with:")
            print(f"  - final_scores: {consultation.final_scores}")
            print(f"  - score_changes: {consultation.score_changes}")
            print(f"  - final_risk_level: {consultation.final_risk_level}")
            print(f"  - improvement_rate: {consultation.improvement_rate}")

            return True

        except Exception as e:
            # 发生错误时回滚，防止脏数据
            db.session.rollback()
            print(f"数据库更新失败: {str(e)}")
            import traceback
            traceback.print_exc()  # 打印完整堆栈跟踪
            return False

    @staticmethod
    def _generate_diagnosis_summary(chat_history, consultation, ai_client, manual=False):
        """
        内部辅助：生成总结 (逻辑从 Route 搬运过来，保持 Service 纯净)
        """
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
    3. **行动建议**：列出医生在对话中给出的具体建议。
    {"4. **备注**：由于患者主动中断了问诊，以上结论可能基于不完整信息。" if manual else ""}

    请直接输出 Markdown 内容。

    【量化评估要求】
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

        # 调用 AI (非流式)
        ai_raw_response = ai_client.get_response(messages)

        # 调用自身的静态方法解析数据
        ConsultationService.update_consultation_data(consultation, ai_raw_response)

        return ai_raw_response

    @staticmethod
    def process_chat_stream(consultation_id, user_content):
        # 1. 初始化
        ai_client = AIClient()
        prompt_builder = PromptBuilder()  # 实例化

        # ... (获取 consultation 对象，校验逻辑保持不变) ...
        consultation = AIConsultation.query.get(consultation_id)
        # ...

        # 2. 更新历史
        history = list(consultation.chat_history)
        history.append({"role": "user", "content": user_content})
        consultation.chat_history = history
        db.session.commit()

        # 3. 【召唤智能体 A：咨询师】
        # 使用 build_consultant_messages 构建上下文
        # 这里的 history 包含了最新的 user_content
        messages = prompt_builder.build_consultant_messages(consultation.report, history)

        full_ai_response = ""
        try:
            # 咨询师参数：温度 0.7 (更像人)
            for chunk in ai_client.get_stream_response(messages, temperature=0.7):
                full_ai_response += chunk
                yield ("message", chunk)

            # ... (处理回复拼接、<END_DIAGNOSIS> 判断逻辑保持不变) ...
            is_finished = "<END_DIAGNOSIS>" in full_ai_response
            clean_response = full_ai_response.replace("<END_DIAGNOSIS>", "").strip()

            history.append({"role": "assistant", "content": clean_response})
            consultation.chat_history = history

            if is_finished:
                # 4. 【召唤智能体 B：分析师】
                # 当对话结束时，不直接用 chat_history 做总结，而是构建专门的 Prompt
                yield ("message", "\n\n[系统] 正在生成专业诊断报告，请稍候...")

                # 传入完整的 history 给分析师
                summary_data = ConsultationService._generate_report_with_agent_b(history, ai_client, prompt_builder)

                # 保存结果 (解析逻辑从 _generate_report_with_agent_b 内部返回)
                consultation.diagnosis_summary = summary_data.get('diagnosis_summary')

                # 自动解析分数并入库 (复用你之前的 update_consultation_data 逻辑，稍作调整)
                if 'scores' in summary_data:
                    # 构造一个伪造的 raw_response 给 update_consultation_data 用，或者直接赋值
                    # 为了复用之前的代码逻辑，这里手动序列化一下
                    fake_raw = json.dumps({"scores": summary_data['scores']})
                    ConsultationService.update_consultation_data(consultation, fake_raw)

                if consultation.report:
                    consultation.report.consultation_status = 'completed'

                db.session.commit()

                yield ("finished", {
                    "consultation_id": consultation.id,
                    "msg": "问诊已结束"
                })
            else:
                db.session.commit()
                yield ("done", "stream_completed")

        except Exception as e:
            # ... (异常处理)
            pass

    @staticmethod
    def _generate_report_with_agent_b(chat_history, ai_client, prompt_builder):
        """
        专门的分析师智能体逻辑
        """
        # 1. 构建 Prompt
        messages = prompt_builder.build_reporter_messages(chat_history)

        # 2. 调用 AI (非流式)
        # 关键：temperature=0.2 (严谨), response_format='json_object' (结构化)
        # 注意：DeepSeek 部分模型支持 response_format={"type": "json_object"}，需要确认 API 文档
        # 如果不支持，temperature=0.1 配合 Prompt 里的 JSON 示例通常也够了
        raw_content = ai_client.get_response(
            messages,
            temperature=0.2,
            response_format={"type": "json_object"}
        )

        # 3. 解析 JSON
        try:
            # 清理一下 markdown code block 标记 (```json ... ```) 以防万一
            clean_json = raw_content.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_json)
            return data
        except json.JSONDecodeError:
            print(f"JSON解析失败，AI返回了: {raw_content}")
            # 兜底：如果 JSON 挂了，返回纯文本作为 summary
            return {"diagnosis_summary": raw_content, "scores": {}}