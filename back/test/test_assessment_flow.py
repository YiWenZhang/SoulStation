import sys
import os

# 路径适配
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src import create_app
from src.extensions import db
from src.models import User, AssessmentSession, AssessmentReport, Question

# ⚠️ 初始化测试环境 APP
app = create_app('testing')


def run_test():
    print("🚀 开始执行 SCL-90 测评全流程测试 (复用 init-data)...")

    with app.app_context():
        # ---------------------------------------------------------
        # 0. 检查数据库连接 & 重置表结构
        # ---------------------------------------------------------
        db_url = app.config.get('SQLALCHEMY_DATABASE_URI')
        print(f"\n📡 当前连接的数据库: 【{db_url}】")

        if 'test' not in str(db_url):
            print("❌ 错误：未连接到测试库！")
            return

        print("🔨 [System] 正在重置测试数据库...")
        db.drop_all()  # 清空旧表
        db.create_all()  # 建新表 (相当于 db upgrade 的最终结果)
        print("✅ 表结构已创建")

        # ---------------------------------------------------------
        # 1. 核心：调用 init-data 命令导入数据
        # ---------------------------------------------------------
        print("\n[Step 1] 正在运行 'flask init-data' 导入基准数据...")

        # 获取命令运行器
        runner = app.test_cli_runner()

        # 🔥🔥🔥 这一句相当于你在终端敲 'flask init-data' 🔥🔥🔥
        result = runner.invoke(args=['init-data'])

        if result.exit_code == 0:
            print(f"✅ 数据导入成功！\n   输出日志: {result.output.strip()}")
        else:
            print(f"❌ 数据导入失败！\n   错误信息: {result.output}")
            # 如果 init-data 失败，可能是因为命令没注册，或者代码有错
            return

        # ---------------------------------------------------------
        # 2. 准备测试用户 (init-data 通常不包含特定测试员，需手动创建)
        # ---------------------------------------------------------
        print("\n[Step 2] 创建本次测试专用用户...")

        # 检查是否已有冲突
        if not User.query.filter_by(phone="13999999999").first():
            test_user = User(
                nickname="自动化测试员",
                phone="13999999999",
                role="user"
            )
            db.session.add(test_user)
            db.session.commit()
            print(f"✅ 测试用户创建成功 (ID: {test_user.id})")
        else:
            test_user = User.query.filter_by(phone="13999999999").first()

        # =========================================================
        # [Step 3] 模拟用户答题 (全自动生成 90 道题的答案)
        # =========================================================
        print("\n[Step 3] 正在全自动生成答卷...")

        import random  # 记得在文件最开头导入，或者这里临时导入

        # 1. 查出数据库里所有的有效题目
        all_questions = Question.query.filter_by(is_enabled=True).all()
        total_count = len(all_questions)
        print(f"   -> 发现数据库共有 {total_count} 道题目")

        # 2. 自动生成答案：{ "题目ID": "随机分(1-5)" }
        #    这样无论数据库里有多少题，都能刚好填满
        chat_history = {
            str(q.id): str(random.randint(1, 5))
            for q in all_questions
        }

        # 3. 创建会话
        session = AssessmentSession(
            user_id=test_user.id,
            total_steps=total_count,
            current_step=total_count,
            status='completed',
            chat_history=chat_history  # 塞入生成的 90 个答案
        )
        db.session.add(session)
        db.session.commit()
        print(f"✅ 会话创建成功 (SessionID: {session.id})，已自动填入 {len(chat_history)} 个答案")
        # ---------------------------------------------------------
        # 4. 测试提交接口
        # ---------------------------------------------------------
        print("\n[Step 4] 测试提交接口 (/submit)...")
        client = app.test_client()

        resp_submit = client.post('/api/assessment/questionnaire/submit', json={
            "session_id": session.id
        })

        report_id = None
        if resp_submit.status_code == 200:
            data = resp_submit.json
            report_id = data['data']['report_id']
            print(f"✅ 提交成功! Report ID: {report_id}")
            print(f"   风险等级: {data['data']['risk_level']}")
        else:
            print(f"❌ 提交失败: {resp_submit.json}")
            return

        # ---------------------------------------------------------
        # 5. 测试详情接口 (验证数据库里的规则是否生效)
        # ---------------------------------------------------------
        print("\n[Step 5] 测试详情接口 (/detail)...")
        resp_detail = client.get(f"/api/assessment/report/detail?report_id={report_id}&uid={test_user.id}")

        if resp_detail.status_code == 200:
            print("✅ 获取详情成功!")
            md = resp_detail.json['data']['content']['advice_md']
            print("\n------ Markdown 预览 ------")
            print(md[:150] + "...")
            print("---------------------------")

            # 如果 init-data 里导入了 assessment_rules，这里就能看到文案了
            if "无法找到" not in md and "暂无说明" not in str(resp_detail.json):
                print("\n✨ 完美！测试成功利用了 init-data 导入的规则数据。")
        else:
            print(f"❌ 获取详情失败: {resp_detail.json}")


if __name__ == '__main__':
    run_test()