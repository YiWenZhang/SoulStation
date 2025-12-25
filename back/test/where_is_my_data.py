import sys
import os
from sqlalchemy import text

# 确保能找到 src
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src import create_app
from src.extensions import db
from src.models import User, AssessmentReport, AssessmentSession

# ==========================================
# 你的目标配置
# ==========================================
TARGET_DB = "soulstation_test"
DB_URI = f"mysql+pymysql://root:123456@127.0.0.1:3306/{TARGET_DB}"


def locate_and_insert():
    print("🚀 启动 GPS 定位脚本...")

    app = create_app('default')

    # 强制覆盖配置
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    with app.app_context():
        # ========================================================
        # 【核心步骤】直接问数据库：你是谁？
        # ========================================================
        try:
            # 这一行会执行 SQL: SELECT DATABASE()
            current_db_name = db.session.execute(text("SELECT DATABASE()")).scalar()
            print("\n" + "!" * 50)
            print(f"📍 [定位结果] 当前 Python 连接的数据库是: 【 {current_db_name} 】")
            print("!" * 50 + "\n")

            if current_db_name != TARGET_DB:
                print(f"❌ 破案了！你想连 '{TARGET_DB}'，但实际上连到了 '{current_db_name}'！")
                print("💡 原因：Flask 的配置覆盖没生效，它用了 config.py 里的默认值。")
                return
            else:
                print("✅ 定位正确，确实连的是测试库。")

        except Exception as e:
            print(f"❌ 连接失败，无法定位: {e}")
            return

        # 如果定位正确，再尝试建表
        print("🏗️  正在建表...")
        db.create_all()

        # 插入一条特征数据
        print("🌱 插入特征数据...")
        user = User(phone="10086", password_hash="123", nickname="GPS测试员", role="user")
        db.session.add(user)
        db.session.commit()

        print(f"✅ 数据已写入库: {current_db_name}")
        print("请立刻去查看这个库。")


if __name__ == "__main__":
    locate_and_insert()