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
        except Exception:
            return None
        return None

    @staticmethod
    def calculate_score_changes(initial_radar_data, final_scores):
        """
        对比初始问卷和 AI 问诊的分数变化
        """
        changes = {}
        # 建立初始分数的查找表
        initial_map = {item['subject']: item['value'] for item in initial_radar_data}

        for dim, new_score in final_scores.items():
            old_score = initial_map.get(dim, 0)
            # 计算变化（保留两位小数）
            changes[dim] = round(new_score - old_score, 2)

        return changes

    @staticmethod
    def update_consultation_data(consultation, ai_raw_response):
        """
        核心封装函数：解析、计算并保存结果到数据库
        """
        # 1. 解析 AI 输出的 JSON
        data = ConsultationService.parse_ai_json_scores(ai_raw_response)
        if not data:
            return False

        try:
            # 2. 提取并更新数据
            final_scores = data.get("scores", {})
            initial_radar = consultation.report.radar_data

            consultation.final_scores = final_scores
            consultation.score_changes = ConsultationService.calculate_score_changes(initial_radar, final_scores)

            # 3. 更新最终风险等级
            max_score = max(final_scores.values()) if final_scores else 0
            if max_score >= 3.0:
                consultation.final_risk_level = 'severe'
            elif max_score >= 2.0:
                consultation.final_risk_level = 'moderate'
            else:
                consultation.final_risk_level = 'good'

            # 4. 【关键】显式通知 SQLAlchemy JSON 字段已修改 (针对部分数据库环境)
            flag_modified(consultation, "final_scores")
            flag_modified(consultation, "score_changes")

            # 5. 【关键】提交事务，写入数据库
            db.session.commit()
            return True

        except Exception as e:
            # 发生错误时回滚，防止脏数据
            db.session.rollback()
            print(f"数据库更新失败: {str(e)}")
            return False