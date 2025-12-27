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
    def build_consultant_messages(self, report, history_messages=None, sequence_number=1, prev_scores=None):
        # 获取通用的系统人设
        base_prompt = self._get_base_system_prompt()

        # 直接从数据库字段组合数据看板
        if sequence_number > 1 and prev_scores:
            data_info = f"""
    【患者数据看板】
    - 原始测评得分：{report.radar_data}
    - 上次 AI 修正得分：{prev_scores}
    - 问诊阶段：第 {sequence_number} 次复诊
    """
            instruction = "请结合上次修正后的分数，重点询问患者近期情绪的变化趋势。"
        else:
            data_info = f"【患者原始测评得分】：{report.radar_data}"
            instruction = "当前为初诊，请基于原始数据进行初步探讨。"

        role_instruction = f"""
    【当前角色任务】
    你现在的身份是“心理咨询师”。
    {data_info}
    {instruction}
    请用温暖、共情、口语化的语气对话。结束请带上 <END_DIAGNOSIS>。
    """

        messages = [{"role": "system", "content": f"{base_prompt}\n{role_instruction}"}]

        # 填充对话历史
        if history_messages:
            messages.extend([m for m in history_messages if m['role'] != 'system'])

        return messages

    # === 智能体 B：分析师 (Reporter) ===
    def build_reporter_messages(self, chat_history, base_scores=None):
        """
        构建【分析师】的上下文
        :param base_scores: 关键！当前对话前的基准分数（初诊为原始分，复诊为上次修正分）
        """
        base_prompt = self._get_base_system_prompt()

        # 1. 转换对话文本
        conversation_text = ""
        for msg in chat_history:
            if msg['role'] in ['user', 'assistant']:
                role = "医生" if msg['role'] == 'assistant' else "患者"
                conversation_text += f"{role}: {msg['content']}\n"

        # 2. 角色指令保持冷静客观
        role_instruction = """
    【当前角色任务】
    你现在的身份是“医疗文书记录员”。请保持绝对客观。
    你的任务是结合“参考基准分数”与“最新的医患对话”，评估患者当前真实的 SCL-90 维度得分。
    """

        # 3. 动态构建任务描述
        user_task = f"""
【对话记录】
{conversation_text}

【输出要求】
返回严格 JSON 格式。

【病历文书 (diagnosis_summary) 生成规范】
1. **排版美观**：使用 Markdown 标题（###）、列表（-）、加粗（**）等符号，确保报告层级清晰。
2. **内容深度**：
   - **现状分析**：不仅总结症状，还要分析患者在对话中展现的深层心理机制。
   - **风险评估**：根据 SCL-90 因子分，给出定性的专业解读。
   - **行动建议**：给出具备可操作性的建议（如特定的认知调整技巧、生活方式建议）。
3. **语言风格**：保持专业、冷静、客观，同时不失人文关怀。

【关键评分指令】
!!重要!! 
1. **对比修正**：请对比上述【参考基准分数】：{base_scores}，根据对话中患者表现出的症状缓解或加重，给出最新的量化得分。
2. **动态体现**：严禁无视基准分数直接打分。如果对话显示某维度有好转，得分应在基准分基础上适当下降；反之上升，一定要有分数波动。
3. **保持连贯**：确保分数的变化趋势符合医疗逻辑。

【JSON 示例】
{{
    "diagnosis_summary": "### 1. 现状分析\\n- **核心症状**：...\\n- **诱发因素**：...\\n\\n### 2. 风险评估\\n...",
    "scores": {{ "焦虑": 2.5, "抑郁": 1.2 }}
}}
"""
        return [
            {"role": "system", "content": f"{base_prompt}\n{role_instruction}"},
            {"role": "user", "content": user_task}
        ]