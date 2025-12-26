import unittest
import json
from src import create_app
from src.extensions import db
from src.models import User, AssessmentReport, AIConsultation, AssessmentSession


class TestConsultationDetail(unittest.TestCase):
    def setUp(self):
        """测试前准备：初始化应用和临时数据库"""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """测试后清理"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_consultation_detail(self):
        """测试获取问诊详情接口"""
        # 1. 创建模拟数据：用户 -> 会话 -> 报告
        user = User(nickname="测试用户")
        db.session.add(user)
        db.session.flush()

        session = AssessmentSession(user_id=user.id, status='completed')
        db.session.add(session)
        db.session.flush()

        # 模拟初始雷达数据
        initial_radar = [
            {"subject": "抑郁", "value": 1.5},
            {"subject": "焦虑", "value": 2.0}
        ]
        report = AssessmentReport(
            session_id=session.id,
            radar_data=initial_radar,
            risk_level='moderate'
        )
        db.session.add(report)
        db.session.flush()

        # 2. 创建模拟 AI 问诊记录
        consultation = AIConsultation(
            report_id=report.id,
            user_id=user.id,
            diagnosis_summary="# 诊断结论\n患者表现出轻微焦虑。",
            final_scores={"抑郁": 1.8, "焦虑": 2.5},
            score_changes={"抑郁": 0.3, "焦虑": 0.5},
            final_risk_level='moderate',
            chat_history=[{"role": "user", "content": "你好"}, {"role": "assistant", "content": "请说"}]
        )
        db.session.add(consultation)
        db.session.commit()

        # 3. 发起请求测试接口
        response = self.client.get(f'/api/consultation/detail/{consultation.id}')
        data = json.loads(response.data)

        # 4. 断言验证
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['code'], 200)

        # 验证返回的核心字段
        res_data = data['data']
        self.assertEqual(res_data['id'], consultation.id)
        self.assertEqual(res_data['diagnosis_summary'], consultation.diagnosis_summary)
        self.assertEqual(res_data['initial_scores'], initial_radar)  # 初始分数
        self.assertEqual(res_data['final_scores']['抑郁'], 1.8)  # AI 分数
        self.assertEqual(res_data['score_changes']['焦虑'], 0.5)  # 变化分
        self.assertEqual(res_data['final_risk_level'], 'moderate')
        self.assertTrue(len(res_data['chat_history']) > 0)

        print("\n✅ 接口测试通过！返回字段完整且数据准确。")


if __name__ == '__main__':
    unittest.main()