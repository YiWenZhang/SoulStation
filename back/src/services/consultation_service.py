from ..extensions import db  # 确保引入了 db 实例
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