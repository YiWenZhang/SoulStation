import json
from ..models import AIAgentConfig, AssessmentRule, AIConsultation


class PromptBuilder:
    def __init__(self):
        # 预定义维度映射：确保雷达图数据的 key 能对应到数据库的中文维度名
        self.DIMENSION_MAPPING = {
            "somatization": "躯体化",
            "obsessive_compulsive": "强迫症状",
            "interpersonal": "人际关系敏感",
            "depression": "抑郁",
            "anxiety": "焦虑",
            "hostility": "敌对",
            "phobic": "恐怖",
            "paranoid": "偏执",
            "psychoticism": "精神病性",
            "diet_sleep": "其他"
        }

    def build_messages(self, report, is_retry=False):
        """
        构建发送给 AI 的完整消息列表 (Messages)
        :param report: AssessmentReport 对象
        :param is_retry: 是否是重试（可选）
        :return: [{"role": "system", ...}, {"role": "user", ...}]
        """
        # 1. 获取 AI 顶层配置 (人设)
        system_prompt = self._get_system_prompt()

        # 2. 构建用户当前的病情描述 (基于规则库)
        patient_status = self._build_patient_status(report)

        # 3. 构建历史病历 (如果是复诊)
        history_context = self._build_history_context(report)

        # 4. 组合最终 User Prompt
        user_content = f"""
【患者当前测评数据】
{patient_status}

【历史诊断记录】
{history_context}

【你的任务】
请基于上述数据，模仿真实的心理医生进行{"复诊" if history_context != "无（初诊）" else "初诊"}。
请直接给出你的分析结论、风险评估和建议，语气要温暖、专业。
"""

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]

    def _get_system_prompt(self):
        """从数据库加载激活的 System Prompt"""
        config = AIAgentConfig.query.filter_by(is_active=True).first()
        if config:
            return config.system_prompt
        # 兜底默认值
        return "你是一名专业的心理咨询师。"

    def _build_patient_status(self, report):
        """
        核心逻辑：不仅给 AI 分数，还要去 AssessmentRule 查具体的症状描述
        """
        status_lines = [
            f"总分：{report.total_score}",
            f"风险等级：{report.risk_level}",
            "--- 详细维度症状 ---"
        ]

        # 解析雷达图数据 (假设是 [{"subject": "抑郁", "value": 3.5}, ...] 或英文 key)
        # 注意：这里需要根据你实际存入 report.radar_data 的格式进行微调
        if not report.radar_data:
            return "暂无详细维度数据"

        radar_list = report.radar_data if isinstance(report.radar_data, list) else []

        for item in radar_list:
            # 兼容前端可能传 "subject" (中文) 或 "name" (英文)
            key = item.get('name') or item.get('subject')  # 比如 'depression' 或 '抑郁'
            score = float(item.get('value') or item.get('score', 0))

            # 1. 尝试获取中文维度名
            cn_dim_name = self.DIMENSION_MAPPING.get(key, key)  # 如果本身是中文就用本身

            # 2. 计算等级 (1-5) 用于查表
            # 简单算法：直接四舍五入或向下取整，这里采用简单的区间判断
            level = int(score)
            if level < 1: level = 1
            if level > 5: level = 5

            # 3. 【关键】去数据库查规则文案
            rule = AssessmentRule.query.filter_by(dimension_name=cn_dim_name, level=level).first()

            desc = rule.description if rule else "存在一定程度的困扰"
            status_lines.append(f"- {cn_dim_name} (得分{score:.1f}): {desc}")

        return "\n".join(status_lines)

    def _build_history_context(self, report):
        """获取上一次 AI 诊断的结论"""
        # 查询该报告关联的最近一次问诊记录
        last_consultation = AIConsultation.query.filter_by(report_id=report.id) \
            .order_by(AIConsultation.created_at.desc()).first()

        if not last_consultation:
            return "无（本次为初诊）"

        return f"""
这是该患者的复诊。
上一次 ({last_consultation.created_at.strftime('%Y-%m-%d')}) AI 医生的诊断结论如下：
-------------------
{last_consultation.diagnosis_summary}
-------------------
请对比本次数据，重点关注症状是否有改善或恶化。
"""