from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate

# 初始化扩展 (暂时不绑定app)
db = SQLAlchemy()
cors = CORS()
socketio = SocketIO()
ma = Marshmallow()
migrate = Migrate()