import pymysql

# 必须和 force_create_db.py 配置一模一样
HOST = '127.0.0.1'
PORT = 3306
USER = 'root'
PASS = '123456'


def get_identity():
    print("🕵️‍♂️ 正在检查 Python 连接的 MySQL 指纹...")
    try:
        conn = pymysql.connect(host=HOST, port=PORT, user=USER, password=PASS)
        cursor = conn.cursor()

        # 获取同样的指纹信息
        cursor.execute("SELECT @@hostname, @@port, @@datadir, database();")
        row = cursor.fetchone()

        print("\n" + "=" * 50)
        print(f"Hostname (主机名): {row[0]}")
        print(f"Port (端口):       {row[1]}")
        print(f"DataDir (数据路径): {row[2]}  <-- 重点看这个！")
        print("=" * 50)

        conn.close()
    except Exception as e:
        print(f"连接失败: {e}")


if __name__ == "__main__":
    get_identity()