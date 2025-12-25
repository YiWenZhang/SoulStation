import pymysql
import sys
import os

# 1. 引入 Flask 环境，确保能找到 models
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src import create_app
from src.extensions import db
# 【重要】必须导入 models，否则 db.create_all() 不知道要建哪些表！
from src.models import User, Question, QuestionOption, QuestionCategory, AssessmentReport, AssessmentSession

# =================配置区域=================
# 请务必确认这里的密码是正确的！
DB_HOST = '127.0.0.1'
DB_PORT = 3306
DB_USER = 'root'
DB_PASS = '123456'
DB_NAME = 'soulstation_test'  # 测试专用库


# ==========================================

def force_init_db():
    print(f"🔥 [1/3] 正在连接 MySQL ({DB_HOST})...")

    # --- 步骤 1: 使用原生驱动创建数据库 (db.create_all 做不到这一步) ---
    try:
        # 连接时不指定 database，只连服务
        conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASS, port=DB_PORT)
        cursor = conn.cursor()

        # 强制删库重演 (保证环境纯净)
        print(f"   -> 正在重置数据库 '{DB_NAME}'...")
        cursor.execute(f"DROP DATABASE IF EXISTS {DB_NAME}")
        cursor.execute(f"CREATE DATABASE {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")

        cursor.close()
        conn.close()
        print(f"✅ [2/3] 数据库 '{DB_NAME}' 创建成功！")

    except Exception as e:
        print(f"❌ MySQL 连接失败: {e}")
        print("💡 请检查: 1.密码对不对? 2.MySQL启动了吗? 3.端口是3306吗?")
        return

    # --- 步骤 2: 使用 Flask-SQLAlchemy 建表 ---
    print(f"🏗️  [3/3] 正在根据 models.py 创建表结构...")

    # 初始化 Flask App
    app = create_app('default')
    # 覆盖配置，连到刚才建好的测试库
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    with app.app_context():
        # 这里会扫描 src/models.py 里定义的所有 Class
        db.create_all()
        print("✅ 表结构创建完毕！")
        print(f"\n🎉 现在你可以去运行测试脚本，或者去 Navicat 查看 '{DB_NAME}' 库了。")


if __name__ == "__main__":
    force_init_db()