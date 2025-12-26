import unittest
import sys
import os
import json

# 1. 确保能导入 src 模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src import create_app, db
from src.models import User, AssessmentReport, AIConsultation, AssessmentSession


class TestStreamChat(unittest.TestCase):
    def setUp(self):
        # 使用 'testing' 配置，但请确保 config.py 或环境变量中有 AI_API_KEY
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # 2. 准备基础数据
        self.user = User(phone='13900000000', nickname='RealTester')
        db.session.add(self.user)
        db.session.commit()

        self.session = AssessmentSession(user_id=self.user.id, status='completed')
        db.session.add(self.session)
        db.session.commit()

        self.report = AssessmentReport(session_id=self.session.id, risk_level='moderate', radar_data={"焦虑": 3.0})
        db.session.add(self.report)
        db.session.commit()

        # 创建一个问诊记录
        self.consultation = AIConsultation(
            report_id=self.report.id,
            user_id=self.user.id,
            chat_history=[
                {"role": "system", "content": "你是一个心理咨询师。"},
                {"role": "assistant", "content": "你好，我是你的AI医生，请问有什么可以帮你？"}
            ],
            sequence_number=1
        )
        db.session.add(self.consultation)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # --- 真实调用测试 (不使用 Mock) ---
    def test_chat_stream_real_api(self):
        print("\n⏳ 正在请求真实 AI 接口，请稍候...")

        # 1. 发起真实请求
        response = self.client.post('/api/consultation/chat/stream', json={
            'consultation_id': self.consultation.id,
            'content': '我最近总是失眠，感觉压力很大，能不能给我一些建议？'  # 真实的用户提问
        })

        # 2. 验证 HTTP 状态
        self.assertEqual(response.status_code, 200)

        # 【关键修改】使用 assertIn 来兼容 'text/event-stream; charset=utf-8'
        self.assertIn('text/event-stream', response.content_type)

        # 3. 验证流式内容 (实时打印效果)
        raw_data = response.data.decode('utf-8')
        lines = raw_data.strip().split('\n\n')

        print(f"📦 收到 {len(lines)} 个数据包 (Token)")

        full_content = ""
        received_done = False
        received_finish = False

        for line in lines:
            if line.startswith("data: "):
                json_str = line.replace("data: ", "")
                try:
                    chunk = json.loads(json_str)

                    if chunk['type'] == 'message':
                        # 拼接 AI 回复的内容
                        print(chunk['content'], end="", flush=True)
                        full_content += chunk['content']

                    elif chunk['type'] == 'done':
                        received_done = True

                    elif chunk['type'] == 'finished':
                        received_finish = True
                        print(f"\n\n[诊断结束] 总结报告 ID: {chunk['content'].get('consultation_id')}")

                except json.JSONDecodeError:
                    pass

        print("\n")

        # 4. 验证是否收到了有效的回复
        self.assertTrue(len(full_content) > 5, "AI 回复内容过短，可能调用失败")

        # 5. 验证数据库是否真实更新
        updated_cons = AIConsultation.query.get(self.consultation.id)
        last_msg = updated_cons.chat_history[-1]

        self.assertEqual(last_msg['role'], 'assistant')
        self.assertIn(full_content[:10], last_msg['content'], "数据库存储的内容应与流式返回的内容一致")

        print("✅ 真实流式接口测试通过！")


if __name__ == '__main__':
    unittest.main()