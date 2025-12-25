import pymysql

# 这里必须和刚才 make_test_data.py 里的配置一模一样
HOST = '127.0.0.1'
PORT = 3306
USER = 'root'
PASS = '123456'
DB_NAME = 'soulstation_test'


def detective():
    print(f"🕵️‍♂️ 侦探开始工作...")
    print(f"目标：{HOST}:{PORT} 用户：{USER}")

    try:
        # 1. 尝试连接数据库
        conn = pymysql.connect(host=HOST, port=PORT, user=USER, password=PASS)
        cursor = conn.cursor()

        # 2. 看看这个 MySQL 里到底有哪些库
        cursor.execute("SHOW DATABASES;")
        all_dbs = [row[0] for row in cursor.fetchall()]
        print(f"\n📂 服务器上的所有数据库: {all_dbs}")

        if DB_NAME not in all_dbs:
            print(f"\n❌ 惊人发现：服务器上根本没有 '{DB_NAME}' 这个库！")
            print("推测：Python 连的可能不是你以为的那个 MySQL (比如你装了两个 MySQL？)")
            return

        # 3. 进入目标库
        conn.select_db(DB_NAME)
        print(f"\n✅ 成功进入数据库 '{DB_NAME}'")

        # 4. 看看有哪些表
        cursor.execute("SHOW TABLES;")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"📄 库里的表: {tables}")

        if not tables:
            print("❌ 库是空的！")
        else:
            if 'assessment_reports' in tables:
                # 5. 查一条数据证明它存在
                cursor.execute("SELECT id, summary_short FROM assessment_reports LIMIT 1;")
                row = cursor.fetchone()
                print(f"\n🎉 找到了！报告表里有数据: {row}")
                print("结论：数据绝对在里面！是你的数据库软件欺骗了你。")
            else:
                print("❌ 有库但没表？")

        conn.close()

    except Exception as e:
        print(f"\n❌ 连接报错: {e}")


if __name__ == "__main__":
    detective()