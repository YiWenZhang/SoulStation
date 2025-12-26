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
        system_prompt = self._get_base_system_prompt()

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



    def _build_patient_status(self, report):
        """
            核心逻辑：支持多种数据格式解析，为 AI 提供精准的风险定性
            """
        raw_data = report.radar_data
        radar_list = []

        # 1. 数据格式标准化处理 (核心修复点)
        if isinstance(raw_data, dict):
            # 兼容你目前的格式: {'抑郁': 1.31, ...}
            # 将其转换为统一的内部处理列表
            radar_list = [{"name": k, "value": v} for k, v in raw_data.items()]
        elif isinstance(raw_data, list):
            # 兼容数组格式: [{"name": "抑郁", "value": 1.31}]
            radar_list = raw_data
        elif isinstance(raw_data, str):
            # 兼容可能的 JSON 字符串格式
            try:
                import json
                parsed = json.loads(raw_data)
                if isinstance(parsed, dict):
                    radar_list = [{"name": k, "value": v} for k, v in parsed.items()]
                else:
                    radar_list = parsed if isinstance(parsed, list) else []
            except:
                radar_list = []

        # 如果仍然没有数据，返回提示
        if not radar_list:
            return "暂无详细维度数据"


        status_lines = []
        max_score = 0.0
        detailed_status = []

        for item in radar_list:
            key = item.get('name') or item.get('subject')
            score = float(item.get('value') or item.get('score', 0))
            max_score = max(max_score, score)

            cn_dim_name = self.DIMENSION_MAPPING.get(key, key)

            # --- 优化点：根据科学区间判定 level ---
            # 假设数据库 AssessmentRule 的 level 1=正常, 2=中轻度, 3=高风险/重度
            if score >= 3.0:
                level = 3  # 高风险
                risk_tag = "【!!高风险/重度!!】"
            elif score >= 2.0:
                level = 2  # 中度
                risk_tag = "【中轻度关注】"
            else:
                level = 1  # 正常
                risk_tag = "【正常】"

            # 去数据库查规则文案
            rule = AssessmentRule.query.filter_by(dimension_name=cn_dim_name, level=level).first()
            desc = rule.description if rule else "存在相关症状困扰"

            detailed_status.append(f"- {cn_dim_name} (得分{score:.2f}): {risk_tag} {desc}")

        # --- 优化点：在头部显式告知 AI 总体结论，防止 AI 误判 ---
        status_lines.append(f"### 测评概况")
        status_lines.append(f"总体风险等级：{report.risk_level.upper()}")  # 'severe'/'moderate'/'good'
        status_lines.append(f"最高因子分：{max_score:.2f}")
        status_lines.append(
            f"风险解读：{'发现重度症状，需立即重点干预' if max_score >= 3.0 else '发现中轻度困扰，建议引导疏导' if max_score >= 2.0 else '心理状态基本良好'}")
        status_lines.append("\n### 详细维度分析")
        status_lines.extend(detailed_status)

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

    def _get_base_system_prompt(self):
        """从数据库获取基础配置 (共性知识：评分规则、SCL-90定义等)"""
        config = AIAgentConfig.query.filter_by(is_active=True).first()
        if config:
            return config.system_prompt
        # 兜底默认值
        return "你是一名专业的心理学专家，熟悉SCL-90量表。"


    # === 智能体 A：咨询师 (Consultant) ===
    def build_consultant_messages(self, report, history_messages=None):
        """
        构建【咨询师】的上下文
        逻辑：数据库基础知识 + 咨询师专属人设
        """
        # 1. 获取数据库里的通用规则 (关键！)
        base_prompt = self._get_base_system_prompt()

        # 2. 追加咨询师专属指令
        role_instruction = """
【当前角色任务】
你现在的身份是“心理咨询师”。
请利用上述规则，用温暖、共情、口语化的语气与患者对话。
不要直接罗列冷冰冰的分数，而是通过对话引导患者表达。
当判断问诊可以结束（如患者表示无话可说，或你已收集足够信息）时，
请务必在回复的最后加上 <END_DIAGNOSIS> 标记。
"""
        final_system_prompt = f"{base_prompt}\n{role_instruction}"

        # 3. 获取患者画像
        patient_status = self._build_patient_status(report)
        user_context = f"【患者当前测评数据】\n{patient_status}\n请基于此数据与患者进行沟通。"

        messages = [{"role": "system", "content": final_system_prompt}]
        messages.append({"role": "user", "content": user_context})

        # 4. 拼接历史
        if history_messages:
            clean_history = [m for m in history_messages if m['role'] != 'system']
            messages.extend(clean_history)

        return messages


    # === 智能体 B：分析师 (Reporter) ===
    def build_reporter_messages(self, chat_history):
        """
        构建【分析师】的上下文
        逻辑：数据库基础知识 + 分析师专属格式要求
        """
        # 1. 获取数据库里的通用规则 (关键！)
        base_prompt = self._get_base_system_prompt()

        # 2. 将对话转为文本供分析
        conversation_text = ""
        for msg in chat_history:
            if msg['role'] in ['user', 'assistant']:
                role = "医生" if msg['role'] == 'assistant' else "患者"
                conversation_text += f"{role}: {msg['content']}\n"

        # 3. 追加分析师专属指令
        role_instruction = """
【当前角色任务】
你现在的身份是“医疗文书记录员”。
请忽略之前的共情要求，保持绝对客观、冷静。
你的任务是阅读医患对话记录，输出一份结构化的 JSON 格式病历。
"""

        user_task = f"""
【对话记录】
{conversation_text}

【输出要求】
请分析上述对话，返回严格的 JSON 数据 (不要Markdown格式)，包含：
1. diagnosis_summary: 包含现状分析、风险评估、行动建议 (Markdown字符串)。
2. scores: 重新评估的 SCL-90 分数 (key为中文维度名, value为数字)。

【JSON示例】
{{
    "diagnosis_summary": "### 现状分析...",
    "scores": {{ "焦虑": 2.5, "抑郁": 1.2 }}
}}
"""
        final_system_prompt = f"{base_prompt}\n{role_instruction}"

        return [
            {"role": "system", "content": final_system_prompt},
            {"role": "user", "content": user_task}
        ]