from flask import Flask
from .extensions import db, cors, socketio, ma, migrate
# 确保 config.py 在根目录下，且能被正确导入
from config import config_map
import os


def create_app(config_name='default'):
    # ===================================================
    # 1. 【核心修复】计算 static 文件夹的绝对路径
    # ===================================================
    # 当前文件在 back/src/，往上两级就是 back/，再拼上 static
    current_dir = os.path.dirname(os.path.abspath(__file__))  # .../back/src
    root_dir = os.path.dirname(current_dir)  # .../back
    static_dir = os.path.join(root_dir, 'static')  # .../back/static

    # 打印路径方便调试，启动时请留意控制台输出
    print(f"📂 静态资源目录设置为: {static_dir}")

    # 如果 static 文件夹不存在，自动创建，防止报错
    if not os.path.exists(static_dir):
        print(f"⚠️ 警告: 静态目录不存在，正在尝试创建...")
        os.makedirs(static_dir)

    # ===================================================
    # 2. 初始化 Flask，显式指定 static_folder
    # ===================================================
    app = Flask(__name__, instance_relative_config=True, static_folder=static_dir)

    app.config.from_object(config_map[config_name])

    # 3. 初始化插件
    db.init_app(app)
    cors.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app, cors_allowed_origins="*")

    # === 【这里一定要加这一句】 ===
    # 让 Flask 知道数据库表结构(models)的存在
    from . import models
    from .models import User

    # ==========================
    # 4. 注册 CLI 命令
    # ==========================
    from .commands import seed_scl90_command, init_ai_config_command
    app.cli.add_command(seed_scl90_command)
    app.cli.add_command(init_ai_config_command)

    # ==========================
    # 5. 注册路由
    # ==========================
    from .routes import register_blueprints
    register_blueprints(app)

    # 【新增】显式注册 AI 问诊接口的 Blueprint
    from .routes.ai_api import ai_bp
    app.register_blueprint(ai_bp)

    return app