import pymysql
import sys
import os

# 添加路径以导入 src
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src import create_app
from src.extensions import db
from src.models import User, Question, QuestionOption, QuestionCategory, AssessmentReport, AssessmentSession

# =================配置区域=================
# 请确认你的 MySQL 密码
DB_HOST = '127.0.0.1'
DB_PORT = 3306
DB_USER = 'root'
DB_PASS = '123456'
DB_NAME = 'soulstation_test'


# ==========================================

def nuke_and_rebuild():
    print(f"💣 [1/4] 正在连接 MySQL 服务器...")

    # 1. 使用 pymysql 直接连接 MySQL (不连具体数据库)，为了删除数据库
    conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASS, port=DB_PORT)
    cursor = conn.cursor()

    # 2. 删除并重建数据库
    print(f"💥 [2/4]正在删除数据库 '{DB_NAME}' (如果存在)...")
    cursor.execute(f"DROP DATABASE IF EXISTS {DB_NAME};")

    print(f"🏗️  [3/4] 正在重新创建数据库 '{DB_NAME}'...")
    cursor.execute(f"CREATE DATABASE {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")

    cursor.close()
    conn.close()
    print("   -> 数据库重建完成！")

    # 3. 使用 Flask-SQLAlchemy 建表和插数据
    print(f"🌱 [4/4] 正在初始化表结构并写入数据...")

    # 重新初始化 App，连接刚才新建的空库
    app = create_app('default')
    new_uri = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    app.config['SQLALCHEMY_DATABASE_URI'] = new_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    with app.app_context():
        # 建表
        db.create_all()

        # --- 插入数据 ---

        # 1. 用户
        user = User(phone="13999999999", password_hash="hash123", nickname="重生之我是测试员", role="user")
        db.session.add(user)
        db.session.commit()

        # 2. 题库分类
        cat = QuestionCategory(name="焦虑")
        db.session.add(cat)
        db.session.commit()

        # 3. 题目
        q1 = Question(stem="彻底重置后感觉如何?", type="single_choice", category_id=cat.id, is_enabled=True)
        db.session.add(q1)
        db.session.commit()

        # 4. 选项
        for i in range(1, 6):
            db.session.add(QuestionOption(question_id=q1.id, label=f"{i}分", score=i))
        db.session.commit()

        # 5. 测评记录
        session = AssessmentSession(user_id=user.id, mode='test', status='completed')
        db.session.add(session)
        db.session.commit()

        # 6. 测评报告
        report = AssessmentReport(
            session_id=session.id,
            summary_short="数据库重置成功",
            risk_level="good",
            radar_data={"焦虑": 1.0},
            detail_content_md="### 成功\n\n数据库已完全重建，数据已写入。"
        )
        db.session.add(report)
        db.session.commit()

        print("\n" + "=" * 50)
        print("✅ 全部完成！")
        print(f"✅ 请去数据库软件(Navicat/DBeaver) 做两件事：")
        print(f"   1. 在连接上右键 -> 刷新 (Refresh)")
        print(f"   2. 打开 '{DB_NAME}' 库 -> 查看 'assessment_reports' 表")
        print("=" * 50)


if __name__ == "__main__":
    try:
        nuke_and_rebuild()
    except Exception as e:
        print(f"\n❌ 失败: {e}")