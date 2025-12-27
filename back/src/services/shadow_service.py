import json
import threading
from flask import current_app
from ..extensions import db
from ..models import AIConsultation
from ..utils.ai_client import AIClient
from ..utils.prompt_builder import PromptBuilder
# 引入新写的 DraftManager
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

                # 2. 【修改点】从文件读取现有草稿 (不再查数据库)
                current_draft = DraftManager.load_draft(consultation_id)

                # 3. 准备对话文本
                dialogue_text = ""
                for msg in recent_history:
                    role = "医生" if msg['role'] == 'assistant' else "患者"
                    dialogue_text += f"{role}: {msg['content']}\n"

                # 4. 调用 AI (逻辑不变)
                messages = prompt_builder.build_shadow_update_messages(current_draft, dialogue_text)

                raw_response = ai_client.get_response(
                    messages,
                    temperature=0.1,
                    response_format={"type": "json_object"}
                )

                # 5. 【修改点】保存更新后的草稿到文件
                try:
                    new_draft = json.loads(raw_response)
                    DraftManager.save_draft(consultation_id, new_draft)
                    print(f"✅ [Shadow Analyst] 临时文件已更新 (ID: {consultation_id})")
                except json.JSONDecodeError:
                    print(f"❌ [Shadow Analyst] JSON 解析失败")

            except Exception as e:
                print(f"❌ [Shadow Analyst] 后台任务出错: {e}")