# back/make_test_data.py
import sys
import os

# 确保能找到 src 模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src import create_app
from src.extensions import db
from src.models import User, Question, QuestionOption, QuestionCategory, AssessmentReport, AssessmentSession
from datetime import datetime

# ==========================================================
# 配置部分：请确保这里的密码是正确的！
# ==========================================================
DB_URI = "mysql+pymysql://root:123456@127.0.0.1:3306/soulstation_test"


def make_data():
    print(f"🚀 [1/5] 正在连接数据库: {DB_URI}")

    # 1. 创建应用上下文
    app = create_app('default')
    app.config.update({
        "SQLALCHEMY_DATABASE_URI": DB_URI,
        "SQLALCHEMY_TRACK_MODIFICATIONS": False
    })

    with app.app_context():
        # 2. 暴力重置：先删光，再重建
        print("🗑️  [2/5] 清理旧表...")
        db.drop_all()

        print("🏗️  [3/5] 创建新表...")
        db.create_all()  # <--- 这一步就是建表！

        # 3. 插入基础数据
        print("🌱 [4/5] 插入基础数据 (用户、题库)...")

        # 用户
        user = User(phone="13800000001", password_hash="hash", nickname="测试用户A", role="user")
        db.session.add(user)
        db.session.commit()  # 提交一次拿到 user.id

        # 维度
        cat = QuestionCategory(name="焦虑")
        db.session.add(cat)
        db.session.commit()

        # 题目
        q1 = Question(stem="最近觉得紧张吗?", type="single_choice", category_id=cat.id, is_enabled=True)
        q2 = Question(stem="无缘无故感到害怕?", type="single_choice", category_id=cat.id, is_enabled=True)
        db.session.add_all([q1, q2])
        db.session.commit()

        # 选项
        for q in [q1, q2]:
            for i in range(1, 6):
                db.session.add(QuestionOption(question_id=q.id, label=f"{i}分", score=i))
        db.session.commit()

        # 4. 手动生成一份报告 (模拟 submit 接口的逻辑)
        print("📝 [5/5] 生成测评报告数据...")

        # 创建 Session
        session = AssessmentSession(
            user_id=user.id,
            mode='questionnaire',
            status='completed',
            total_steps=2,
            current_step=2,
            chat_history={str(q1.id): 4, str(q2.id): 5}  # 假装选了高分
        )
        db.session.add(session)
        db.session.commit()

        # 创建 Report (手动写死 Markdown，模拟生成结果)
        report = AssessmentReport(
            session_id=session.id,
            summary_short="中度焦虑风险",
            risk_level="moderate",
            radar_data={"焦虑": 4.5},
            high_risk_dimensions=["焦虑"],
            detail_content_md="### 1. 整体状态总结\n\n测试数据生成成功！如果您能在数据库看到这段话，说明表结构没问题。\n\n### 2. 建议\n\n快去数据库看看吧！"
        )
        db.session.add(report)
        db.session.commit()

        print("\n" + "=" * 50)
        print(f"✅ 数据生成完毕！")
        print(f"✅ 请去数据库 '{DB_URI.split('/')[-1]}' 查看以下表：")
        print(f"   - users (用户表)")
        print(f"   - assessment_reports (报告表，重点看这个)")
        print(f"   - questions (题目表)")
        print("=" * 50)


if __name__ == "__main__":
    try:
        make_data()
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        print("💡 提示: 请检查数据库密码是否正确，以及数据库 'soulstation_test' 是否已创建。")