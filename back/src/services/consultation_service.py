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
            initial_radar = {}
            if consultation.report and consultation.report.radar_data:
                initial_radar = consultation.report.radar_data
                if isinstance(initial_radar, str):
                    try:
                        initial_radar = json.loads(initial_radar)
                    except:
                        initial_radar = {}

            print(f"Debug: Initial radar data from report: {initial_radar}")

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
    def process_chat_stream(consultation_id, user_content):
        """
        核心业务流：处理对话 -> 流式返回 -> 自动存档 -> 触发总结
        返回一个生成器，生成 (event_type, data) 元组
        """
        # 1. 初始化工具
        ai_client = AIClient()

        # 2. 获取并校验数据
        consultation = AIConsultation.query.get(consultation_id)
        if not consultation:
            yield ("error", "Consultation not found")
            return

        if consultation.diagnosis_summary:
            yield ("error", "Consultation finished")
            return

        # 3. 更新对话历史 (用户部分)
        history = list(consultation.chat_history)
        history.append({"role": "user", "content": user_content})

        # 临时保存用户输入，防止流中断导致消息丢失
        consultation.chat_history = history
        db.session.commit()

        # 4. 调用 AI 流式接口
        full_ai_response = ""
        try:
            # 这里的 yield 将实时推送到 Controller
            for chunk in ai_client.get_stream_response(history):
                full_ai_response += chunk
                # 实时返回内容块
                yield ("message", chunk)

            # 5. 流结束后处理：拼接完整回复
            is_finished = "<END_DIAGNOSIS>" in full_ai_response
            clean_response = full_ai_response.replace("<END_DIAGNOSIS>", "").strip()

            # 更新历史 (AI 部分)
            history.append({"role": "assistant", "content": clean_response})
            consultation.chat_history = history

            if is_finished:
                # --- 触发结束逻辑 (原 route 中的逻辑移到这里) ---
                summary = ConsultationService._generate_diagnosis_summary(history, consultation, ai_client)

                consultation.diagnosis_summary = summary
                if consultation.report:
                    consultation.report.consultation_status = 'completed'

                db.session.commit()

                # 通知前端结束，并附带总结ID等信息
                yield ("finished", {
                    "consultation_id": consultation.id,
                    "msg": "问诊已自动结束并生成报告"
                })
            else:
                # 普通对话结束
                db.session.commit()
                yield ("done", "stream_completed")

        except Exception as e:
            db.session.rollback()
            yield ("error", str(e))

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