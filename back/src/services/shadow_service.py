import json
import threading
from flask import current_app
from ..extensions import db
from ..models import AIConsultation
from ..utils.ai_client import AIClient
from ..utils.prompt_builder import PromptBuilder
from ..utils.draft_manager import DraftManager


class ShadowService:
    @staticmethod
    def trigger_shadow_analysis(app, consultation_id, recent_history):
        thread = threading.Thread(
            target=ShadowService._run_analysis_task,
            args=(app, consultation_id, recent_history)
        )
        thread.start()

    @staticmethod
    def _run_analysis_task(app, consultation_id, recent_history):
        with app.app_context():
            try:
                # 1. 初始化
                ai_client = AIClient()
                prompt_builder = PromptBuilder()

                # 2. 读取现有草稿 (如果不存在则为空字典)
                current_draft = DraftManager.load_draft(consultation_id)
                if not current_draft:
                    current_draft = {}

                # 3. 准备对话文本
                dialogue_text = ""
                for msg in recent_history:
                    role = "医生" if msg['role'] == 'assistant' else "患者"
                    dialogue_text += f"{role}: {msg['content']}\n"

                # 4. 调用 AI
                messages = prompt_builder.build_shadow_update_messages(current_draft, dialogue_text)

                # 这里的 response_format 已经在 AIClient 里修复支持了
                raw_response = ai_client.get_response(
                    messages,
                    temperature=0.1,
                    response_format={"type": "json_object"}
                )

                # 5. 【核心修复】深度合并逻辑 (Deep Merge)
                # 不直接覆盖，而是将 partial_update 合并进 current_draft
                try:
                    partial_update = json.loads(raw_response)

                    # 定义合并函数：递归地更新字典
                    def deep_merge(target, source):
                        for key, value in source.items():
                            # 如果双方都是字典，则递归合并
                            if isinstance(value, dict) and key in target and isinstance(target[key], dict):
                                deep_merge(target[key], value)
                            else:
                                # 否则直接覆盖（即更新了某个维度的分值或摘要）
                                target[key] = value
                        return target

                    # 执行合并：current_draft 会被就地更新
                    updated_draft = deep_merge(current_draft, partial_update)

                    # 保存完整的 draft
                    DraftManager.save_draft(consultation_id, updated_draft)
                    print(f"✅ [Shadow Analyst] 临时文件已更新 (增量合并模式)")

                except json.JSONDecodeError:
                    print(f"❌ [Shadow Analyst] JSON 解析失败: {raw_response[:50]}...")

            except Exception as e:
                print(f"❌ [Shadow Analyst] 后台任务出错: {e}")