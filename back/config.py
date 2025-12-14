import os
from dotenv import load_dotenv

# 获取当前文件的绝对路径 (即 back 文件夹路径)
basedir = os.path.abspath(os.path.dirname(__file__))

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-very-secret'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 允许所有来源跨域
    CORS_ALLOWED_ORIGINS = "*"

class DevelopmentConfig(Config):
    DEBUG = True
    # 路径中增加了 'instance'
    # 最终结果：sqlite:///.../back/instance/soulstation.db
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'soulstation.db')

class ProductionConfig(Config):
    DEBUG = False
    # 生产环境数据库也放在 instance 下
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'data.sqlite')

config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}