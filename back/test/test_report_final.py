import unittest
import sys
import os

# 确保能导入 src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import create_app
from src.extensions import db
from src.models import User, Question, QuestionOption, QuestionCategory


class FinalReportTestCase(unittest.TestCase):
    def setUp(self):
        """初始化：连接测试库，准备数据"""
        # 使用 'testing' 配置 (连接 soulstation_test)
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        print("\n>>> [1/4] 正在重置测试数据库...")
        db.drop_all()  # 先清空旧数据
        db.create_all()  # 建新表

        # === 1. 造用户 ===
        self.user = User(phone="13900000001", password_hash="hash", nickname="测试员小张", role="user")
        db.session.add(self.user)
        db.session.commit()

        # === 2. 造题库 (焦虑维度) ===
        self.cat = QuestionCategory(name="焦虑")
        db.session.add(self.cat)
        db.session.commit()

        # 造 3 道题，以便测试完整性校验
        self.questions = []
        for i in range(1, 4):
            q = Question(stem=f"测试题目{i}: 你感到焦虑吗?", type="single_choice", category_id=self.cat.id,
                         is_enabled=True)
            db.session.add(q)
            self.questions.append(q)
        db.session.commit()

        # 造选项
        for q in self.questions:
            for i in range(1, 6):
                db.session.add(QuestionOption(question_id=q.id, label=f"{i}分", score=i))
        db.session.commit()
        print(">>> [2/4] 基础数据准备完毕 (用户 + 3道题目)")

    def tearDown(self):
        """测试结束：关键步骤——不删库！"""
        db.session.remove()
        # db.drop_all()  <-- 【关键】注释掉这一行，保留现场！
        self.app_context.pop()
        print("\n" + "=" * 50)
        print("✅ 测试结束！数据已保留在 'soulstation_test' 库中。")
        print("请去数据库查看 'assessment_reports' 表。")
        print("=" * 50)

    def test_generate_and_view_report(self):
        """流程测试：答题 -> 提交 -> 查看详情"""

        # 1. 开始测评
        res = self.client.post('/api/assessment/questionnaire/start', json={"uid": self.user.id, "action": "new"})
        session_id = res.get_json()['data']['session_id']

        # 2. 模拟答题 (全选 4 分，制造“中度风险”)
        answers = {}
        for q in self.questions:
            answers[str(q.id)] = 4

        self.client.post('/api/assessment/questionnaire/save', json={
            "session_id": session_id,
            "answers": answers
        })

        # 3. 提交测评 (生成报告)
        print(">>> [3/4] 正在提交测评...")
        submit_res = self.client.post('/api/assessment/questionnaire/submit', json={"session_id": session_id})
        self.assertEqual(submit_res.status_code, 200, f"提交失败: {submit_res.get_json().get('msg')}")

        report_id = submit_res.get_json()['data']['report_id']
        print(f"    -> 报告生成成功！ID: {report_id}")

        # 4. 调用新增接口：获取详情
        print(">>> [4/4] 正在验证 'get_report_detail' 接口...")
        detail_res = self.client.get('/api/assessment/report/detail', query_string={
            'uid': self.user.id,
            'report_id': report_id
        })

        self.assertEqual(detail_res.status_code, 200)
        data = detail_res.get_json()['data']

        # 验证返回结构
        self.assertEqual(data['base_info']['user_name'], "测试员小张")
        self.assertEqual(data['core_result']['risk_level'], 'moderate')

        # 打印生成的 Markdown 看看
        print(f"\n[生成的 Markdown 预览]\n{'-' * 30}")
        print(data['content']['advice_md'])
        print(f"{'-' * 30}")


if __name__ == '__main__':
    unittest.main()

# 运行以上测试文件
# 进入测试数据库可以查看报告
# SELECT detail_content_md FROM assessment_reports ORDER BY id DESC LIMIT 1 \G