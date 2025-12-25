import unittest
from src import create_app
from src.extensions import db
from src.models import User, Question, QuestionOption, QuestionCategory


class ReportDetailTestCase(unittest.TestCase):
    def setUp(self):
        """测试前置：初始化环境和数据库"""
        # =====================================================
        # 【修改点】直接使用 'testing' 配置
        # 这样 create_app 内部就会直接连接 soulstation_test
        # =====================================================
        self.app = create_app('testing')

        # 不需要再手动 update config 了，删掉之前那一大段 app.config.update 代码

        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        # 确保连接的是测试库 (现在肯定是了)
        # 建议先 drop_all 清空旧数据，再 create_all
        db.drop_all()
        db.create_all()
        # === 1. 准备基础数据 (用户) ===
        self.user_a = User(phone="13800000001", password_hash="hash", nickname="UserA", role="user")
        self.user_b = User(phone="13900000002", password_hash="hash", nickname="UserB", role="user")

        db.session.add_all([self.user_a, self.user_b])
        db.session.commit()

        # === 2. 准备基础数据 (题目与维度) ===
        self.cat = QuestionCategory(name="焦虑")
        db.session.add(self.cat)
        db.session.commit()

        # 创建 2 道题目
        self.q1 = Question(stem="觉得紧张?", type="single_choice", category_id=self.cat.id, is_enabled=True)
        self.q2 = Question(stem="感到恐慌?", type="single_choice", category_id=self.cat.id, is_enabled=True)
        db.session.add_all([self.q1, self.q2])
        db.session.commit()

        # 添加选项
        for q in [self.q1, self.q2]:
            for i in range(1, 6):
                db.session.add(QuestionOption(question_id=q.id, label=f"{i}分", score=i))
        db.session.commit()

    def tearDown(self):
        """测试结束：清理数据"""
        db.session.remove()
        # db.drop_all()  # 跑完把表删了，保持环境干净
        self.app_context.pop()

    # ... (create_report_for_user 和下面的测试用例代码完全不用动，保持原样即可) ...
    # 辅助函数：快速生成一份报告
    def create_report_for_user(self, user):
        res = self.client.post('/api/assessment/questionnaire/start', json={"uid": user.id, "action": "new"})
        session_id = res.get_json()['data']['session_id']

        answers = {str(self.q1.id): 4, str(self.q2.id): 5}
        self.client.post('/api/assessment/questionnaire/save', json={"session_id": session_id, "answers": answers})

        submit_res = self.client.post('/api/assessment/questionnaire/submit', json={"session_id": session_id})
        return submit_res.get_json()['data']['report_id']

    def test_get_detail_success(self):
        report_id = self.create_report_for_user(self.user_a)
        response = self.client.get('/api/assessment/report/detail', query_string={
            'uid': self.user_a.id, 'report_id': report_id
        })
        self.assertEqual(response.status_code, 200)
        res_data = response.get_json()['data']

        # 验证 Markdown
        md_content = res_data['content']['advice_md']
        print(f"\n[MySQL Test] 生成的 Markdown 预览: {md_content[:30]}...")
        self.assertIn("###", md_content)

    def test_unauthorized_access(self):
        report_id_a = self.create_report_for_user(self.user_a)
        response = self.client.get('/api/assessment/report/detail', query_string={
            'uid': self.user_b.id, 'report_id': report_id_a
        })
        self.assertEqual(response.status_code, 403)

    def test_missing_parameters(self):
        response = self.client.get('/api/assessment/report/detail')
        self.assertEqual(response.status_code, 400)

    def test_report_not_found(self):
        response = self.client.get('/api/assessment/report/detail', query_string={
            'uid': self.user_a.id, 'report_id': 999999
        })
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()