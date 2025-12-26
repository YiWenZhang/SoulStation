import unittest
import json
from unittest.mock import patch
from src import create_app
from src.extensions import db
from src.models import User, AssessmentReport, AssessmentSession, AIConsultation
from src.utils.init_data import init_all_data


class TestAIConsultationFlow(unittest.TestCase):
    def setUp(self):
        """测试环境初始化：构建内存数据库及测试桩数据"""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()
        init_all_data()  # 初始化PromptBuilder所需的人设和知识库

        # 1. 创建测试用户
        self.user = User(nickname='Tester', phone='13900001111', password_hash='hash', role='user')
        db.session.add(self.user)
        db.session.commit()

        # 2. 创建测评会话与原始报告 (提供初始雷达图分数)
        self.session = AssessmentSession(user_id=self.user.id, mode='questionnaire', status='completed')
        db.session.add(self.session)
        db.session.commit()

        self.report = AssessmentReport(
            session_id=self.session.id,
            risk_level='moderate',
            radar_data={"躯体化": 2.0, "抑郁": 2.5, "焦虑": 2.2},  # 初始分数
            consultation_status='none'
        )
        db.session.add(self.report)
        db.session.commit()
        self.report_id = self.report.id

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    @patch('src.utils.ai_client.AIClient.get_response')
    def test_ai_auto_finish_and_db_write(self, mock_ai):
        """
        测试场景 1：AI 识别对话内容并主动触发 <END_DIAGNOSIS>
        验证：状态流转为 finished，数据库写入 final_scores 和 final_risk_level
        """
        # 模拟 AI 的两次返回：1. 开启问诊回复；2. 触发结束的回复（带量化数据）
        mock_ai.side_effect = [
            "你好，我是AI医生，请问哪里不舒服？",
            "明白了。你的情况属于轻度焦虑。<END_DIAGNOSIS>",  # 模拟触发结束
            # 以下是 _generate_diagnosis_summary 内部调用的 Mock 返回，包含结构化总结和 JSON
            """# 诊断建议\n建议多休息。
            {"scores": {"躯体化": 1.5, "抑郁": 2.0, "焦虑": 3.5}}"""
        ]

        # 1. 发起问诊
        start_res = self.client.post('/api/consultation/start', json={'report_id': self.report_id})
        consult_id = start_res.json['consultation_id']

        # 2. 对话并触发 AI 自动结束
        chat_res = self.client.post('/api/consultation/chat', json={
            'consultation_id': consult_id,
            'content': '我最近压力很大，心跳很快'
        })

        # 3. 断言接口返回
        self.assertEqual(chat_res.status_code, 200)
        self.assertEqual(chat_res.json['status'], 'finished')
        self.assertIn("问诊已自动结束", chat_res.json['msg'])

        # 4. 验证数据库写入结果
        consultation = AIConsultation.query.get(consult_id)
        report = AssessmentReport.query.get(self.report_id)

        self.assertIsNotNone(consultation.diagnosis_summary)
        self.assertEqual(report.consultation_status, 'completed')
        # 验证量化分数是否正确解析（由 ConsultationService 处理）
        self.assertEqual(consultation.final_scores.get('焦虑'), 3.5)
        # 验证风险等级是否根据 3.5 分更新为 severe
        self.assertEqual(consultation.final_risk_level, 'severe')
        # 验证分数变化是否计算 (3.5 - 2.2 = 1.3)
        self.assertAlmostEqual(consultation.score_changes.get('焦虑'), 1.3)

    @patch('src.utils.ai_client.AIClient.get_response')
    def test_manual_finish_flow(self, mock_ai):
        """
        测试场景 2：用户点击按钮手动结束问诊
        验证：调用 /finish 接口强制生成报告并入库
        """
        mock_ai.side_effect = [
            "你好，我们可以开始。环境如何？",
            # 修改下面的字符串，加上测试断言需要的文字
            """# 阶段总结
            由于患者主动中断了问诊，以上结论可能基于不完整信息。
            {"scores": {"躯体化": 1.0, "抑郁": 1.0, "焦虑": 1.0}}"""
        ]

        # 1. 启动问诊
        start_res = self.client.post('/api/consultation/start', json={'report_id': self.report_id})
        consult_id = start_res.json['consultation_id']

        # 2. 模拟用户直接点击“结束问诊”按钮
        finish_res = self.client.post('/api/consultation/finish', json={'consultation_id': consult_id})

        # 3. 断言响应
        self.assertEqual(finish_res.status_code, 200)
        self.assertEqual(finish_res.json['status'], 'finished')

        # 4. 验证数据库
        consultation = AIConsultation.query.get(consult_id)
        self.assertIn("由于患者主动中断", consultation.diagnosis_summary)  # 验证 manual=True 的逻辑
        self.assertEqual(consultation.final_risk_level, 'good')  # 1.0分应为 'good'

    def test_get_detail_api(self):
        """
        测试场景 3：获取问诊详情接口
        验证：已结束的问诊能够正确返回对比数据
        """
        # 手动向数据库存入一条已完成的问诊
        cons = AIConsultation(
            report_id=self.report_id,
            user_id=self.user.id,
            sequence_number=1,
            diagnosis_summary="测试总结内容",
            final_scores={"抑郁": 4.0},
            final_risk_level="severe",
            chat_history=[{"role": "assistant", "content": "hello"}]
        )
        db.session.add(cons)
        db.session.commit()

        res = self.client.get(f'/api/consultation/detail/{cons.id}')
        data = res.json['data']

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['final_risk_level'], 'severe')
        self.assertEqual(data['initial_scores']['抑郁'], 2.5)  # 对应 setUp 里的初始值
        self.assertEqual(data['status'], 'finished')


if __name__ == '__main__':
    unittest.main()