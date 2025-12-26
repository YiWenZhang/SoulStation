"""
test_ai_consultation_fixed.py
修复了AIConsultation没有report属性的问题
"""
import sys
import os
import json
import unittest
from unittest.mock import patch, MagicMock

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 先创建简化的模型类，避免导入所有复杂模型
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, JSON, ForeignKey, DateTime, Float, Boolean
from datetime import datetime
from sqlalchemy.orm import relationship

# 创建测试用的简化模型
db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    phone = Column(String(20), unique=True, index=True)
    nickname = Column(String(50))


class AssessmentSession(db.Model):
    __tablename__ = 'assessment_sessions'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    mode = Column(String(20), default='ai_chat')
    status = Column(String(20), default='ongoing')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    report = relationship('AssessmentReport', backref='session', uselist=False)


class AssessmentReport(db.Model):
    __tablename__ = 'assessment_reports'
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('assessment_sessions.id'), unique=True, nullable=False)
    summary_short = Column(String(255))
    radar_data = Column(JSON)
    risk_level = Column(String(20))
    total_score = Column(Float, default=0.0)
    consultation_count = Column(Integer, default=0)
    consultation_status = Column(String(20), default='none')
    generated_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    consultations = relationship('AIConsultation', backref='report', lazy='dynamic')


class AIConsultation(db.Model):
    __tablename__ = 'ai_consultations'
    id = Column(Integer, primary_key=True)
    report_id = Column(Integer, ForeignKey('assessment_reports.id'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    sequence_number = Column(Integer, default=1, comment='问诊次序')
    chat_history = Column(JSON, default=list)
    diagnosis_summary = Column(Text, comment='本次AI生成的诊断总结与建议')
    final_scores = Column(JSON, nullable=True)
    score_changes = Column(JSON, nullable=True)
    final_risk_level = Column(String(20), nullable=True)
    improvement_rate = Column(Float, nullable=True)
    current_step = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# 导入需要测试的服务
from src.services.consultation_service import ConsultationService


class TestAIConsultationFixed(unittest.TestCase):
    """修复了AIConsultation没有report属性的测试"""

    def setUp(self):
        """测试前设置"""
        # 创建测试Flask应用
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        # 初始化数据库
        db.init_app(self.app)

        with self.app.app_context():
            db.create_all()

        self.client = self.app.test_client()

    def tearDown(self):
        """测试后清理"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def _create_test_data(self):
        """创建测试数据并返回相关对象"""
        with self.app.app_context():
            # 创建测试用户
            test_user = User(
                phone='13800138000',
                nickname='测试用户'
            )
            db.session.add(test_user)

            # 创建测评会话
            test_session = AssessmentSession(
                user_id=test_user.id,
                mode='questionnaire',
                status='completed'
            )
            db.session.add(test_session)

            # 创建测评报告
            test_report = AssessmentReport(
                session_id=test_session.id,
                summary_short='测试报告摘要',
                radar_data={
                    "躯体化": 2.5,
                    "强迫症状": 2.1,
                    "人际关系敏感": 1.8,
                    "抑郁": 1.3,
                    "焦虑": 2.0,
                    "敌对": 1.7,
                    "恐怖": 1.7,
                    "偏执": 1.8,
                    "精神病性": 2.8,
                    "其他": 2.3
                },
                risk_level='moderate',
                total_score=20.0,
                consultation_count=0
            )
            db.session.add(test_report)

            # 创建AI问诊记录
            test_consultation = AIConsultation(
                report_id=test_report.id,
                user_id=test_user.id,
                sequence_number=1,
                chat_history=[
                    {"role": "system", "content": "你是心理医生"},
                    {"role": "assistant", "content": "你好，我是AI心理医生"}
                ],
                current_step=1
            )
            db.session.add(test_consultation)

            # 提交所有更改
            db.session.commit()

            # 刷新对象以确保关系加载
            db.session.refresh(test_consultation)
            db.session.refresh(test_report)

            return test_user, test_session, test_report, test_consultation

    def test_parse_ai_json_scores(self):
        """测试解析AI返回的JSON分数"""
        test_response = """
        患者表现出一定的焦虑症状，建议放松训练。

        {
          "scores": {
            "躯体化": 2.25,
            "强迫症状": 2.10,
            "抑郁": 1.31,
            "焦虑": 2.10
          }
        }
        """

        result = ConsultationService.parse_ai_json_scores(test_response)
        self.assertIsNotNone(result)
        self.assertIn('scores', result)
        self.assertEqual(result['scores']['焦虑'], 2.10)

    def test_calculate_score_changes(self):
        """测试计算分数变化"""
        initial_data = {
            "躯体化": 2.5,
            "焦虑": 2.0,
            "抑郁": 1.3
        }

        final_scores = {
            "躯体化": 2.25,
            "焦虑": 2.10,
            "抑郁": 1.31
        }

        changes = ConsultationService.calculate_score_changes(initial_data, final_scores)

        self.assertIn("躯体化", changes)
        self.assertIn("焦虑", changes)
        self.assertIn("抑郁", changes)

        # 验证计算是否正确
        self.assertAlmostEqual(changes["躯体化"], -0.25)  # 2.25 - 2.5 = -0.25
        self.assertAlmostEqual(changes["焦虑"], 0.10)  # 2.10 - 2.0 = 0.10
        self.assertAlmostEqual(changes["抑郁"], 0.01)  # 1.31 - 1.3 = 0.01

    def test_update_consultation_data_success(self):
        """测试成功更新咨询数据"""
        ai_response = """
        患者情况有所改善。

        {
          "scores": {
            "躯体化": 2.25,
            "焦虑": 2.10,
            "抑郁": 1.31
          }
        }
        """

        with self.app.app_context():
            # 创建测试数据
            _, _, test_report, test_consultation = self._create_test_data()

            # 验证关系是否正确建立
            self.assertIsNotNone(test_consultation.report, "consultation应该有关联的report")
            self.assertEqual(test_consultation.report.id, test_report.id)

            # 初始验证
            self.assertIsNone(test_consultation.final_scores)
            self.assertIsNone(test_consultation.score_changes)
            self.assertIsNone(test_consultation.final_risk_level)

            # 调用更新方法
            result = ConsultationService.update_consultation_data(test_consultation, ai_response)

            self.assertTrue(result, "更新应该成功")

            # 验证数据库已更新
            db.session.refresh(test_consultation)
            self.assertIsNotNone(test_consultation.final_scores)
            self.assertIsNotNone(test_consultation.score_changes)
            self.assertIsNotNone(test_consultation.final_risk_level)

            # 验证具体数据
            self.assertEqual(test_consultation.final_scores['焦虑'], 2.10)
            self.assertEqual(test_consultation.final_risk_level, 'moderate')  # max_score=2.25

            # 验证分数变化
            self.assertIn("躯体化", test_consultation.score_changes)
            self.assertIn("焦虑", test_consultation.score_changes)
            self.assertIn("抑郁", test_consultation.score_changes)

            # 验证报告数据仍然存在
            self.assertIsNotNone(test_consultation.report.radar_data)

    def test_update_consultation_data_with_full_scores(self):
        """测试使用完整分数更新咨询数据"""
        ai_response = """
        完整的评估报告。

        {
          "scores": {
            "躯体化": 2.25,
            "强迫症状": 2.10,
            "人际关系敏感": 1.78,
            "抑郁": 1.31,
            "焦虑": 2.10,
            "敌对": 1.67,
            "恐怖": 1.71,
            "偏执": 1.83,
            "精神病性": 2.80,
            "其他": 2.29
          }
        }
        """

        with self.app.app_context():
            # 创建测试数据
            _, _, test_report, test_consultation = self._create_test_data()

            # 验证关系
            self.assertIsNotNone(test_consultation.report)

            result = ConsultationService.update_consultation_data(test_consultation, ai_response)

            self.assertTrue(result, "更新应该成功")

            db.session.refresh(test_consultation)

            # 验证所有维度都保存了
            self.assertEqual(len(test_consultation.final_scores), 10)

            # 验证风险等级计算
            self.assertEqual(test_consultation.final_risk_level, 'severe')  # max_score=2.80

            # 验证分数变化计算
            self.assertEqual(len(test_consultation.score_changes), 10)

    def test_update_consultation_data_failure(self):
        """测试更新咨询数据失败的情况（无效的JSON）"""
        invalid_response = "这不是有效的JSON响应"

        with self.app.app_context():
            # 创建测试数据
            _, _, test_report, test_consultation = self._create_test_data()

            # 验证关系
            self.assertIsNotNone(test_consultation.report)

            result = ConsultationService.update_consultation_data(test_consultation, invalid_response)

            self.assertFalse(result, "无效JSON应该导致更新失败")

            # 验证数据未更新
            db.session.refresh(test_consultation)
            self.assertIsNone(test_consultation.final_scores)
            self.assertIsNone(test_consultation.score_changes)

    def test_risk_level_calculation(self):
        """测试风险等级计算"""
        test_cases = [
            # (scores, expected_risk_level)
            ({"焦虑": 1.5, "抑郁": 1.2}, "good"),  # 最高分 < 2.0
            ({"焦虑": 2.0, "抑郁": 1.8}, "moderate"),  # 最高分 >= 2.0 且 < 3.0
            ({"焦虑": 2.5, "抑郁": 2.1}, "moderate"),  # 最高分 >= 2.0 且 < 3.0
            ({"焦虑": 3.0, "抑郁": 2.5}, "severe"),  # 最高分 >= 3.0
            ({"焦虑": 3.5, "抑郁": 1.5}, "severe"),  # 最高分 >= 3.0
        ]

        for scores, expected_risk_level in test_cases:
            ai_response = f"""
            测试报告。

            {json.dumps({"scores": scores})}
            """

            with self.app.app_context():
                # 创建测试数据
                _, _, test_report, test_consultation = self._create_test_data()

                # 验证关系
                self.assertIsNotNone(test_consultation.report)

                result = ConsultationService.update_consultation_data(test_consultation, ai_response)
                self.assertTrue(result, f"更新应该成功: {scores}")

                db.session.refresh(test_consultation)
                self.assertEqual(
                    test_consultation.final_risk_level,
                    expected_risk_level,
                    f"分数 {scores} 应该得到风险等级 {expected_risk_level}"
                )

    def test_end_to_end_consultation_flow(self):
        """测试完整的问诊流程"""
        # 模拟AI对话和结束
        ai_end_response = """
        根据对话分析，患者情况有所好转。
        建议：继续放松训练。

        {
          "scores": {
            "躯体化": 2.0,
            "焦虑": 1.8,
            "抑郁": 1.2
          }
        }
        """

        with self.app.app_context():
            # 创建测试数据
            _, _, test_report, test_consultation = self._create_test_data()

            # 验证关系
            self.assertIsNotNone(test_consultation.report)

            # 1. 初始状态
            self.assertIsNone(test_consultation.diagnosis_summary)
            self.assertIsNone(test_consultation.final_scores)
            self.assertIsNone(test_consultation.score_changes)
            self.assertIsNone(test_consultation.final_risk_level)

            # 2. 执行更新（模拟结束问诊）
            result = ConsultationService.update_consultation_data(test_consultation, ai_end_response)
            self.assertTrue(result, "结束问诊更新应该成功")

            # 3. 手动设置诊断总结（模拟实际流程）
            test_consultation.diagnosis_summary = "诊断总结内容"
            db.session.commit()

            # 4. 验证最终状态
            db.session.refresh(test_consultation)
            self.assertIsNotNone(test_consultation.diagnosis_summary)
            self.assertIsNotNone(test_consultation.final_scores)
            self.assertIsNotNone(test_consultation.score_changes)
            self.assertIsNotNone(test_consultation.final_risk_level)

            # 5. 验证具体数据
            self.assertEqual(test_consultation.final_scores['焦虑'], 1.8)
            self.assertEqual(test_consultation.final_risk_level, 'good')  # max_score=2.0

    def test_improvement_rate_calculation(self):
        """测试改进率计算"""
        ai_response = """
        评估报告。

        {
          "scores": {
            "躯体化": 2.0,
            "焦虑": 1.5,
            "抑郁": 1.0
          }
        }
        """

        with self.app.app_context():
            # 创建测试数据
            _, _, test_report, test_consultation = self._create_test_data()

            # 验证关系
            self.assertIsNotNone(test_consultation.report)

            # 计算初始总分
            initial_total = sum(test_report.radar_data.values())

            result = ConsultationService.update_consultation_data(test_consultation, ai_response)
            self.assertTrue(result)

            db.session.refresh(test_consultation)

            # 验证改进率存在
            self.assertIsNotNone(test_consultation.improvement_rate)

            # 计算期望的改进率
            final_total = sum(test_consultation.final_scores.values())
            expected_rate = round((initial_total - final_total) / initial_total * 100, 1)

            # 由于浮点数精度，允许微小差异
            self.assertAlmostEqual(
                test_consultation.improvement_rate,
                expected_rate,
                places=1,
                msg=f"改进率计算错误: {test_consultation.improvement_rate} vs {expected_rate}"
            )

    def test_database_write_verification(self):
        """验证数据确实写入数据库"""
        ai_response = """
        测试数据写入。

        {
          "scores": {
            "焦虑": 2.5,
            "抑郁": 2.0
          }
        }
        """

        with self.app.app_context():
            # 创建测试数据
            _, _, test_report, test_consultation = self._create_test_data()
            consultation_id = test_consultation.id

            # 验证关系
            self.assertIsNotNone(test_consultation.report)

            # 执行更新
            result = ConsultationService.update_consultation_data(test_consultation, ai_response)
            self.assertTrue(result)

            # 强制提交并关闭当前会话
            db.session.commit()
            db.session.remove()

            # 重新查询，验证数据持久化
            new_consultation = AIConsultation.query.get(consultation_id)

            # 验证数据确实保存了
            self.assertIsNotNone(new_consultation.final_scores)
            self.assertIsNotNone(new_consultation.score_changes)
            self.assertIsNotNone(new_consultation.final_risk_level)

            self.assertEqual(new_consultation.final_scores['焦虑'], 2.5)
            self.assertEqual(new_consultation.final_risk_level, 'moderate')

    def test_score_changes_calculation_accuracy(self):
        """验证分数变化计算的准确性"""
        with self.app.app_context():
            # 创建测试数据
            _, _, test_report, test_consultation = self._create_test_data()

            # 模拟AI返回的分数
            ai_response = """
            测试准确性。

            {
              "scores": {
                "躯体化": 2.25,
                "焦虑": 2.10,
                "抑郁": 1.31
              }
            }
            """

            result = ConsultationService.update_consultation_data(test_consultation, ai_response)
            self.assertTrue(result)

            db.session.refresh(test_consultation)

            # 手动计算期望的变化
            expected_changes = {}
            for dim, final_score in test_consultation.final_scores.items():
                initial_score = test_report.radar_data.get(dim, 0)
                expected_changes[dim] = round(final_score - initial_score, 2)

            # 验证计算正确
            for dim, expected_change in expected_changes.items():
                actual_change = test_consultation.score_changes.get(dim)
                self.assertEqual(
                    actual_change,
                    expected_change,
                    f"维度 {dim} 的变化计算错误: {actual_change} vs {expected_change}"
                )


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)