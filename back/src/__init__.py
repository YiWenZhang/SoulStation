from flask import Flask
from .extensions import db, cors, socketio, ma, migrate
from config import config_map

def create_app(config_name='default'):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_map[config_name])

    # 1. 初始化插件
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
    # 2. 注册 CLI 命令 (新增)
    # ==========================
    from .commands import seed_scl90_command, init_ai_config_command  # 导入我们在 commands.py 定义的函数
    app.cli.add_command(seed_scl90_command)  # 注册到 flask 命令集中
    app.cli.add_command(init_ai_config_command)  # 注册新命令
    # ==========================
    # 3. 注册路由
    from .routes import register_blueprints
    register_blueprints(app)
    # 【新增】显式注册 AI 问诊接口的 Blueprint
    # 这样 Flask 才能识别 /api/consultation/... 的请求
    from .routes.ai_api import ai_bp
    app.register_blueprint(ai_bp)

    return app