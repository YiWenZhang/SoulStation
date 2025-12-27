from flask import current_app
from .shadow_service import ShadowService
from ..utils.draft_manager import DraftManager
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
    def process_chat_stream(consultation_id, user_content):
        # 获取 real_app 传给后台线程
        real_app = current_app._get_current_object()
        # 1. 初始化
        ai_client = AIClient()
        prompt_builder = PromptBuilder()  # 实例化
        # ... (获取 consultation 对象，校验逻辑保持不变) ...
        consultation = AIConsultation.query.get(consultation_id)
        if not consultation: return
        # ...

        # 2. 更新历史
        history = list(consultation.chat_history)
        history.append({"role": "user", "content": user_content})
        consultation.chat_history = history
        db.session.commit()

        # 3. 【召唤智能体 A：咨询师】
        # 使用 build_consultant_messages 构建上下文
        # 这里的 history 包含了最新的 user_content
        # --- 新增逻辑：获取上一次的分数作为复诊依据 ---
        prev_scores = None
        if consultation.sequence_number > 1:
            # 查找同一份报告下的上一次问诊记录
            prev_con = AIConsultation.query.filter_by(
                report_id=consultation.report_id,
                sequence_number=consultation.sequence_number - 1
            ).first()
            if prev_con:
                prev_scores = prev_con.final_scores

        # --- 修改点：传入 sequence_number 和 prev_scores ---
        # 这里的 history 包含了最新的 user_content
        messages = prompt_builder.build_consultant_messages(
            consultation.report,
            history,
            sequence_number=consultation.sequence_number,  # 传入序号
            prev_scores=prev_scores  # 传入上次 AI 分数
        )

        full_ai_response = ""
        try:
            # 咨询师参数：温度 0.7 (更像人)
            # === Agent A 流式输出 ===
            for chunk in ai_client.get_stream_response(messages, temperature=0.7):
                full_ai_response += chunk
                yield ("message", chunk)

            # ... (处理回复拼接、<END_DIAGNOSIS> 判断逻辑保持不变) ...
            is_finished = "<END_DIAGNOSIS>" in full_ai_response
            clean_response = full_ai_response.replace("<END_DIAGNOSIS>", "").strip()

            # =======================================================
            # 【核心修改区】 在保存前进行过滤
            # =======================================================

            # 1. 先把 AI 的最新回复加到内存列表里
            history.append({"role": "assistant", "content": clean_response})

            # 2. 定义过滤规则：只保留真正的用户对话和 AI 回复
            # 过滤掉 'system' 角色
            # 过滤掉 包含 '【患者当前测评数据】' 的 prompt 上下文 (因为 PromptBuilder 下次会自动重新生成它，不用存)

            clean_history_to_save = []
            for msg in history:
                # 规则1: 只要不是 system 角色
                if msg.get('role') == 'system':
                    continue

                # 规则2: 如果是 user 角色，但内容是后端自动拼装的“测评数据”，也不要存
                # 判断依据可以是内容特征，比如包含 "【患者当前测评数据】"
                if msg.get('role') == 'user' and "【患者当前测评数据】" in msg.get('content', ''):
                    continue

                clean_history_to_save.append(msg)

            # 3. 将干净的历史存入数据库
            consultation.chat_history = clean_history_to_save
            db.session.commit()
            # =================================================
            # 【优化点 1】触发 Agent B (影子模式) - 实时更新
            # =================================================
            if not is_finished:
                # 提取最近一轮对话，丢给影子去分析
                recent_round = [
                    {"role": "user", "content": user_content},
                    {"role": "assistant", "content": clean_response}
                ]
                # 异步执行，不卡顿
                ShadowService.trigger_shadow_analysis(real_app, consultation_id, recent_round)

            # =================================================
            # 【优化点 2】触发 Agent B (报告模式) - 极速交卷
            # =================================================
            if is_finished:
                yield ("message", "\n\n[系统] 正在基于实时草稿生成最终报告...")

                # 直接调用下面的私有方法生成报告
                # 注意：这里我们不需要传 history 了，因为信息都在 draft 里
                summary_data = ConsultationService._generate_report_with_agent_b(
                    consultation_id,  # 传 ID 方便去读文件
                    ai_client,
                    prompt_builder,
                    consultation
                )

                # 保存结果 (复用原有逻辑)
                consultation.diagnosis_summary = summary_data.get('diagnosis_summary')

                if 'scores' in summary_data:
                    fake_raw = json.dumps({"scores": summary_data['scores']})
                    ConsultationService.update_consultation_data(consultation, fake_raw)

                if consultation.report:
                    consultation.report.consultation_status = 'completed'

                db.session.commit()

                # 【扫尾】清理临时文件
                DraftManager.delete_draft(consultation_id)

                yield ("finished", {
                    "consultation_id": consultation.id,
                    "msg": "问诊已结束"
                })
            else:
                yield ("done", "stream_completed")

        except Exception as e:
            # ... 异常处理
            pass

        # =====================================================
        # 辅助方法修改：改为从草稿读取
        # =====================================================

    @staticmethod
    def _generate_report_with_agent_b(consultation_id, ai_client, prompt_builder, consultation):
        """
        原来的生成报告逻辑 -> 升级为读取 DraftManager
        """
        # 1. 确定基准分数 (逻辑不变)
        base_scores = consultation.report.radar_data
        if consultation.sequence_number > 1:
            prev_con = AIConsultation.query.filter_by(
                report_id=consultation.report_id,
                sequence_number=consultation.sequence_number - 1
            ).first()
            if prev_con and prev_con.final_scores:
                base_scores = prev_con.final_scores

        # 2. 【核心修改】从文件加载影子分析师写好的草稿
        draft_data = DraftManager.load_draft(consultation_id)

        # 如果草稿是空的（比如只有一句话就结束了），兜底策略：把当前简单的对话作为草稿
        if not draft_data:
            draft_data = {"overview": "对话较短，未生成详细草稿", "chat_log": "请直接分析历史记录"}

        # 3. 构建 Prompt (使用升级后的 build_reporter_messages)
        messages = prompt_builder.build_reporter_messages(draft_data, base_scores=base_scores)

        # 4. 调用 AI (JSON 模式)
        raw_content = ai_client.get_response(
            messages,
            temperature=0.2,
            response_format={"type": "json_object"}
        )

        # 5. 解析
        try:
            clean_json = raw_content.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_json)
        except:
            return {"diagnosis_summary": raw_content, "scores": {}}

'''
    @staticmethod
    def _generate_report_with_agent_b(chat_history, ai_client, prompt_builder, consultation):
        """
        专门的分析师智能体逻辑：重写版，支持动态传入基准分数
        """
        # 1. 自动确定分析基准：
        # 如果是复诊 (sequence_number > 1)，基准是上一轮 AI 修正后的 final_scores
        # 如果是初诊，基准是 report 里的原始 radar_data
        base_scores = None
        if consultation.sequence_number > 1:
            # 查找上一轮问诊记录
            prev_con = consultation.__class__.query.filter_by(
                report_id=consultation.report_id,
                sequence_number=consultation.sequence_number - 1
            ).first()

            if prev_con and prev_con.final_scores:
                base_scores = prev_con.final_scores
                # 兼容处理 JSON 字符串情况
                if isinstance(base_scores, str):
                    try:
                        base_scores = json.loads(base_scores)
                    except:
                        base_scores = consultation.report.radar_data
            else:
                # 没找到上一轮分数则退回原始数据
                base_scores = consultation.report.radar_data
        else:
            # 初诊直接使用原始数据
            base_scores = consultation.report.radar_data

        # 2. 构建 Prompt：将 base_scores 传给分析师 B 的提示词生成方法
        messages = prompt_builder.build_reporter_messages(chat_history, base_scores=base_scores)

        # 3. 调用 AI (非流式)
        # temperature=0.2 保持严谨，response_format 强制要求 JSON
        raw_content = ai_client.get_response(
            messages,
            temperature=0.2,
            response_format={"type": "json_object"}
        )

        # 4. 解析 JSON 结果
        try:
            # 清理 Markdown 代码块标记（如果有）
            clean_json = raw_content.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_json)

            # 即使 AI 返回的是 {"scores": {...}}，外层也需要这个结构
            return data
        except json.JSONDecodeError:
            print(f"JSON解析失败，分析师B返回了: {raw_content}")
            # 兜底处理
            return {
                "diagnosis_summary": raw_content,
                "scores": base_scores  # 报错时至少保留基准分数不丢失
            }
'''