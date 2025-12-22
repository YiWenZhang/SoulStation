import os
from dotenv import load_dotenv

# 获取当前文件的绝对路径
basedir = os.path.abspath(os.path.dirname(__file__))

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-very-secret'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CORS_ALLOWED_ORIGINS = "*"

    # === 【新增】管理员注册密钥 ===
    # 在生产环境中，建议将此密钥放入 .env 文件中
    ADMIN_SECRET_KEY = os.environ.get('ADMIN_SECRET_KEY') or 'SoulStation2025_Admin'


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'mysql+pymysql://root:123456@localhost:3306/soulstation_db'


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or \
                              'sqlite:///' + os.path.join(basedir, 'instance', 'data.sqlite')


config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}