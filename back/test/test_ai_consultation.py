import unittest
import json
import time
from unittest.mock import patch
from src import create_app
from src.extensions import db
from src.models import User, AssessmentReport, AssessmentSession, AIConsultation
from src.utils.init_data import init_all_data


class TestAIConsultation(unittest.TestCase):
    def setUp(self):
        """测试环境初始化"""
        # 如果只想在内存中跑测试，改为 'testing'
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        # 1. 确保数据库表存在
        db.create_all()

        # 2. 初始化 AI 配置 (人设、知识库)
        # 这一步不可省略，否则 PromptBuilder 没数据
        init_all_data()

        # 3. 创建测试用户 (适配你的 models.py)
        test_phone = '13800000088'  # 使用一个特殊的测试号
        self.user = User.query.filter_by(phone=test_phone).first()

        if not self.user:
            self.user = User(
                nickname='AI测试员',
                phone=test_phone,
                password_hash='fake_hash_123',  # 你的模型用的是 password_hash
                role='user'
            )
            db.session.add(self.user)
            db.session.commit()
            print(f">>> 创建新用户 ID: {self.user.id}")
        else:
            print(f">>> 复用已有用户 ID: {self.user.id}")

        # 4. 创建测评会话 (Session)
        # Report 必须依赖 Session，Session 必须依赖 User
        self.session = AssessmentSession(
            user_id=self.user.id,
            mode='questionnaire',
            status='completed',
            total_steps=90,
            current_step=90
        )
        db.session.add(self.session)
        db.session.commit()

        # 5. 创建测评报告 (Report)
        self.report = AssessmentReport(
            session_id=self.session.id,
            total_score=250.0,  # 模拟高分
            risk_level='high',  # 你的模型字段是 String(20)
            high_risk_dimensions=["depression", "sleep", "anxiety"],
            # 模拟雷达图数据 (确保 key 对应 prompt_builder 里的映射)
            radar_data=[
                {"name": "depression", "value": 4.5},
                {"name": "anxiety", "value": 3.8},
                {"name": "sleep", "value": 4.2}
            ],
            consultation_status='none'
        )
        db.session.add(self.report)
        db.session.commit()

        self.report_id = self.report.id
        print(f">>> 准备就绪: Report ID {self.report_id}")

    def tearDown(self):
        """清理环境"""
        # 为了让你能在数据库里看到结果，我们只提交，不删除
        db.session.commit()
        print(">>> 测试结束，数据已保留在数据库中 (user phone: 13800000088)")

        # 如果你想每次都清空，取消下面两行的注释：
        # db.session.remove()
        # db.drop_all()

        self.app_context.pop()

    # =================================================================
    # 测试用例
    # =================================================================

    # 如果想用真实 AI，请注释掉下面这行 @patch
    # @patch('src.utils.ai_client.AIClient.get_response')
    def test_consultation_flow(self, mock_ai=None):
        """测试：开启 -> 对话 -> 结束"""

        # --- Mock 配置 (如果启用了 @patch) ---
        if mock_ai:
            print("\n>>> [模拟模式] 使用 Mock 数据")
            mock_ai.side_effect = [
                "你好，我是你的AI心理顾问。我看到你最近睡眠和情绪都不太好，能具体聊聊吗？",  # start
                "我理解这种痛苦。这种情况持续多久了？<END_DIAGNOSIS>",  # chat (触发结束)
                "# 诊断报告\n\n**风险评估**：高风险。\n**建议**：立刻就医。"  # summary
            ]
        else:
            print("\n>>> [真机模式] 调用真实 AI API (请耐心等待)...")

        # 1. 发起问诊
        print("\n[1] 请求 /api/consultation/start ...")
        res1 = self.client.post('/api/consultation/start', json={
            'report_id': self.report_id
        })
        self.assertEqual(res1.status_code, 200, f"Start failed: {res1.text}")
        data1 = res1.json
        consult_id = data1['consultation_id']
        print(f"    -> AI: {data1['message']}")

        # 2. 发送消息
        print("\n[2] 请求 /api/consultation/chat ...")
        user_msg = "我感觉非常糟糕，整晚睡不着，白天也没力气，持续两周了。"
        res2 = self.client.post('/api/consultation/chat', json={
            'consultation_id': consult_id,
            'content': user_msg
        })
        self.assertEqual(res2.status_code, 200, f"Chat failed: {res2.text}")
        data2 = res2.json
        print(f"    -> AI: {data2['message']}")

        # 3. 检查是否结束
        if data2.get('status') == 'finished':
            print("\n[3] AI 自动触发了结束协议")
            print(f"    -> 报告预览: {data2['report'][:50]}...")
        else:
            print("\n[3] 手动调用 /api/consultation/finish ...")
            res3 = self.client.post('/api/consultation/finish', json={
                'consultation_id': consult_id
            })
            self.assertEqual(res3.status_code, 200)
            data3 = res3.json
            print(f"    -> 报告预览: {data3['report'][:50]}...")


if __name__ == '__main__':
    unittest.main()