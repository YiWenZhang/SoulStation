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
    # ==========================
    # 2. 注册路由
    from .routes import register_blueprints
    register_blueprints(app)

    return app