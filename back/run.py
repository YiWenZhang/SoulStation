import os
from src import create_app
from src.extensions import socketio

# 默认为开发环境，部署改为生产环境
config_name = os.environ.get('FLASK_CONFIG', 'default')
app = create_app(config_name)

if __name__ == '__main__':
    # 获取真实的数据库路径配置
    db_path = app.config.get('SQLALCHEMY_DATABASE_URI', '未知路径')

    print(f"--- SoulStation 后端启动中 [{config_name}] ---")
    print(f"--- 数据库位置: {db_path} ---")

    # debug=True 可以在代码修改后自动重启
    socketio.run(app, port=5000, debug=True)