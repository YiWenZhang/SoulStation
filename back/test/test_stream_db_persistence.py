import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json

# 路径配置，确保能导入 src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src import create_app, db
from src.models import User, AssessmentReport, AIConsultation, AssessmentSession


class TestStreamDBPersistence(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # --- 准备测试数据 ---
        self.user = User(phone='13999999999', nickname='DBTester')
        db.session.add(self.user)
        db.session.commit()

        self.session = AssessmentSession(user_id=self.user.id, status='completed')
        db.session.add(self.session)
        db.session.commit()

        self.report = AssessmentReport(session_id=self.session.id, risk_level='low', radar_data={"焦虑": 1.0})
        db.session.add(self.report)
        db.session.commit()

        # 初始只有一条 System 消息
        self.consultation = AIConsultation(
            report_id=self.report.id,
            user_id=self.user.id,
            chat_history=[{"role": "system", "content": "System Prompt"}],
            sequence_number=1,
            diagnosis_summary=None  # 初始为空
        )
        db.session.add(self.consultation)
        db.session.commit()

        self.cons_id = self.consultation.id

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # ================================================================
    # 测试点 1: 验证普通对话是否成功写入 chat_history
    # ================================================================
    @patch('src.services.consultation_service.AIClient')
    def test_normal_chat_persistence(self, MockAIClient):
        print("\n[Test 1] 验证普通对话入库...")

        # 1. 模拟 AI 返回流
        mock_instance = MockAIClient.return_value

        def mock_generator(messages):
            yield "AI"
            yield "收到"

        mock_instance.get_stream_response.side_effect = mock_generator

        # 2. 发起请求
        response = self.client.post('/api/consultation/chat/stream', json={
            'consultation_id': self.cons_id,
            'content': '用户发送测试消息123'
        })

        # 3. 必须消费完流，后端才会执行完入库逻辑
        for _ in response.data:
            pass

            # 4. 【核心验证】查询数据库
        # 注意：一定要重新从 DB 查，不要用 self.consultation 缓存
        updated_cons = AIConsultation.query.get(self.cons_id)
        history = updated_cons.chat_history

        # 验证长度：初始1 + 用户1 + AI1 = 3
        self.assertEqual(len(history), 3, "历史记录长度应为3")

        # 验证内容
        self.assertEqual(history[1]['role'], 'user')
        self.assertEqual(history[1]['content'], '用户发送测试消息123')

        self.assertEqual(history[2]['role'], 'assistant')
        self.assertEqual(history[2]['content'], 'AI收到')

        print("✅ 普通对话：用户输入和 AI 回复均已持久化到数据库")

    # ================================================================
    # 测试点 2: 验证触发结束时，是否生成总结并更新状态
    # ================================================================
    @patch('src.services.consultation_service.AIClient')
    def test_finish_trigger_persistence(self, MockAIClient):
        print("\n[Test 2] 验证结束总结入库...")

        mock_instance = MockAIClient.return_value

        # 1. 模拟 AI 流式输出结束标记
        def mock_end_generator(messages):
            yield "再见。"
            yield "<END_DIAGNOSIS>"

        mock_instance.get_stream_response.side_effect = mock_end_generator

        # 2. 模拟 Service 内部调用 get_response 生成总结
        # 这是 process_chat_stream 内部在检测到 END 标签后调用的
        mock_instance.get_response.return_value = "## 最终医疗诊断书\n\n患者情况稳定..."

        # 3. 发起请求
        response = self.client.post('/api/consultation/chat/stream', json={
            'consultation_id': self.cons_id,
            'content': '我没事了，谢谢'
        })

        # 4. 消费流
        content = response.data.decode('utf-8')

        # 5. 【核心验证】数据库状态
        updated_cons = AIConsultation.query.get(self.cons_id)

        # 验证总结字段是否被填充
        self.assertIsNotNone(updated_cons.diagnosis_summary)
        self.assertIn("最终医疗诊断书", updated_cons.diagnosis_summary)

        # 验证关联的 Report 状态是否变为 completed
        self.assertEqual(updated_cons.report.consultation_status, 'completed')

        print("✅ 结束流程：诊断总结已生成，问诊状态已更新为 completed")


if __name__ == '__main__':
    unittest.main()