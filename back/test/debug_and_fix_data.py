import sys
import os

# 确保能找到 src 模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src import create_app
from src.extensions import db
from src.models import User, Question, QuestionOption, QuestionCategory, AssessmentReport, AssessmentSession

# =================配置区域=================
REAL_DB_URI = "mysql+pymysql://root:123456@127.0.0.1:3306/soulstation_test"


# ==========================================

def fix_and_make_data():
    print(f"🚀 启动程序...")

    # 1. 创建 App
    app = create_app('default')

    # 2. 强制更新配置
    app.config['SQLALCHEMY_DATABASE_URI'] = REAL_DB_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    with app.app_context():
        # 3. 【核心测谎环节】获取当前实际使用的引擎 URL
        current_url = str(db.engine.url)
        print(f"\n🔍 [测谎仪] Flask 认为它连的是: {current_url}")

        # 如果发现是 sqlite，说明 update 晚了，需要强制重置
        if 'sqlite' in current_url or 'memory' in current_url:
            print(f"⚠️  警告：发现连接的是 SQLite！正在尝试强制切换到 MySQL...")
            # 强制销毁旧引擎，迫使下次操作使用新配置创建连接
            db.get_engine(app).dispose()

            # 再次检查
            new_url = str(db.engine.url)
            print(f"🔄 [重置后] 现在连的是: {new_url}")

            if 'mysql' not in new_url:
                print("❌ 切换失败，请检查 config.py 是否写死了配置。")
                return

        # 4. 开始造数据
        print("\n🏗️  开始重建数据库...")
        db.drop_all()
        db.create_all()
        print("✅ 表结构创建成功！")

        # 插入数据
        print("🌱 插入演示数据...")
        user = User(phone="13800000001", password_hash="hash", nickname="TestUser", role="user")
        db.session.add(user)
        db.session.commit()

        cat = QuestionCategory(name="焦虑")
        db.session.add(cat)
        db.session.commit()

        q1 = Question(stem="测试题目1", type="single_choice", category_id=cat.id, is_enabled=True)
        db.session.add(q1)
        db.session.commit()

        # 生成报告
        session = AssessmentSession(user_id=user.id, mode='questionnaire', status='completed')
        db.session.add(session)
        db.session.commit()

        report = AssessmentReport(
            session_id=session.id,
            summary_short="测试报告",
            risk_level="moderate",
            radar_data={"焦虑": 4.0},
            detail_content_md="### 成功！\n\n如果您看到这条数据，说明终于连上 MySQL 了！"
        )
        db.session.add(report)
        db.session.commit()

        print("\n" + "=" * 50)
        print(f"🎉 成功！数据已写入: {REAL_DB_URI}")
        print("请立刻去数据库刷新查看 'assessment_reports' 表。")
        print("=" * 50)


if __name__ == "__main__":
    try:
        fix_and_make_data()
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")