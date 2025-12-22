import unittest
from src import create_app
from src.extensions import db
from src.models import User, AssessmentSession, AssessmentReport, Question, QuestionOption, QuestionCategory


class QuestionnaireTestCase(unittest.TestCase):
    def setUp(self):
        """测试前置：初始化App、数据库和基础数据"""
        self.app = create_app('default')
        # 使用内存数据库进行测试，速度快且不污染环境
        self.app.config.update({
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False
        })

        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # === 1. 准备基础数据 ===
        # 创建测试用户
        self.user = User(phone="13800000001", password_hash="hash", nickname="TestUser", role="user")
        db.session.add(self.user)
        db.session.commit()

        # 创建维度
        self.cat_anxiety = QuestionCategory(name="焦虑")
        db.session.add(self.cat_anxiety)
        db.session.commit()

        # === 2. 准备题目 ===
        # 我们只创建 2 道题，方便测试“全答完”和“没答完”的场景
        self.q1 = Question(stem="题目1：感到紧张?", type="single_choice", category_id=self.cat_anxiety.id,
                           is_enabled=True)
        self.q2 = Question(stem="题目2：感到害怕?", type="single_choice", category_id=self.cat_anxiety.id,
                           is_enabled=True)
        db.session.add_all([self.q1, self.q2])
        db.session.commit()

        # 为每道题创建选项 (1-5分)
        for q in [self.q1, self.q2]:
            for i in range(1, 6):
                opt = QuestionOption(question_id=q.id, label=f"{i}分", score=i)
                db.session.add(opt)
        db.session.commit()

        # 记录当前题库总数，用于后续断言
        self.total_questions = 2

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # ==========================================
    # 测试用例
    # ==========================================

    def test_submit_incomplete_fail(self):
        """测试：如果有题目没做，提交应该失败 (400)"""
        # 1. 开启测评
        res = self.client.post('/api/assessment/questionnaire/start', json={"uid": self.user.id, "action": "new"})
        session_id = res.get_json()['data']['session_id']

        # 2. 只回答第 1 题 (总共 2 题)
        answers = {str(self.q1.id): 3}
        self.client.post('/api/assessment/questionnaire/save', json={
            "session_id": session_id,
            "answers": answers
        })

        # 3. 尝试提交
        submit_res = self.client.post('/api/assessment/questionnaire/submit', json={"session_id": session_id})
        data = submit_res.get_json()

        # 4. 验证：应该被拒绝
        print(f"\n[测试漏选] 返回信息: {data['msg']}")
        self.assertEqual(submit_res.status_code, 400)
        self.assertIn("未完成", data['msg'])
        # 验证返回的数据详情
        self.assertEqual(data['data']['answered'], 1)
        self.assertEqual(data['data']['total'], 2)

    def test_submit_complete_success(self):
        """测试：答完所有题目，提交成功 (200)"""
        # 1. 开启测评
        res = self.client.post('/api/assessment/questionnaire/start', json={"uid": self.user.id, "action": "new"})
        session_id = res.get_json()['data']['session_id']

        # 2. 回答所有题目 (2道题都答)
        answers = {
            str(self.q1.id): 4,  # 偏重
            str(self.q2.id): 5  # 严重
        }
        self.client.post('/api/assessment/questionnaire/save', json={
            "session_id": session_id,
            "answers": answers
        })

        # 3. 提交
        submit_res = self.client.post('/api/assessment/questionnaire/submit', json={"session_id": session_id})
        data = submit_res.get_json()

        # 4. 验证：成功生成报告
        print(f"\n[测试成功] 报告ID: {data.get('data', {}).get('report_id')}")
        self.assertEqual(submit_res.status_code, 200)
        self.assertEqual(data['msg'], "报告生成成功")

        # 验证数据库状态
        report = AssessmentReport.query.filter_by(session_id=session_id).first()
        self.assertIsNotNone(report)
        # 验证算分：(4+5)/2 = 4.5
        self.assertEqual(report.radar_data.get('焦虑'), 4.5)

    def test_save_and_resume(self):
        """补充测试：验证实时保存后，重新进入能回显答案 (断点续传)"""
        # 1. 开启测评
        res = self.client.post('/api/assessment/questionnaire/start', json={"uid": self.user.id, "action": "new"})
        session_id = res.get_json()['data']['session_id']

        # 2. 保存进度：第1题选 5分
        self.client.post('/api/assessment/questionnaire/save', json={
            "session_id": session_id,
            "answers": {str(self.q1.id): 5}
        })

        # 3. 模拟用户刷新页面或退出后重新进来 (action='check')
        resume_res = self.client.post('/api/assessment/questionnaire/start',
                                      json={"uid": self.user.id, "action": "check"})
        data = resume_res.get_json()

        # 4. 验证
        print(f"\n[测试回显] 状态: {data['msg']}")
        # 应该是恢复存档模式
        self.assertEqual(data['data']['is_resumed'], True)
        # 之前保存的答案应该还在
        saved_score = data['data']['answers_snapshot'].get(str(self.q1.id))
        self.assertEqual(saved_score, 5)  # 验证取出来的值确实是 5

if __name__ == '__main__':
    unittest.main()