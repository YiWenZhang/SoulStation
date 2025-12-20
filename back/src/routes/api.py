from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import secrets
from ..extensions import db
from ..models import User

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/test', methods=['GET'])
def test_api():
    return jsonify({
        "code": 200,
        "msg": "后端环境连接成功！(SQLite)",
        "data": None
    })


# ==========================================
# 1. 注册接口 (Register)
# ==========================================
@api_bp.route('/auth/register', methods=['POST'])
def register():
    # 获取前端传来的 JSON 数据
    data = request.get_json()
    if not data:
        return jsonify({"code": 400, "msg": "请提供注册信息"}), 400

    phone = data.get('phone')
    password = data.get('password')
    nickname = data.get('nickname', f"用户{phone[-4:]}")  # 默认昵称

    # 简单校验
    if not phone or not password:
        return jsonify({"code": 400, "msg": "手机号和密码不能为空"}), 400

    # 检查手机号是否已存在
    if User.query.filter_by(phone=phone).first():
        return jsonify({"code": 400, "msg": "该手机号已注册，请直接登录"}), 400

    # 创建新用户
    try:
        new_user = User(
            phone=phone,
            nickname=nickname,
            # 【重要】密码必须加密存储，不能存明文！
            password_hash=generate_password_hash(password),
            avatar_url="https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png"  # 默认头像
        )

        db.session.add(new_user)
        db.session.commit()

        return jsonify({"code": 200, "msg": "注册成功，请登录"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "msg": f"注册失败: {str(e)}"}), 500


# ==========================================
# 2. 登录接口 (Login)
# ==========================================
@api_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    phone = data.get('phone')
    password = data.get('password')

    if not phone or not password:
        return jsonify({"code": 400, "msg": "请输入账号密码"}), 400

    # 查找用户
    user = User.query.filter_by(phone=phone).first()

    # 验证密码 (将输入的明文密码加密后与数据库比对)
    if user and check_password_hash(user.password_hash, password):

        # 更新最后登录时间
        user.last_login_at = datetime.utcnow()
        db.session.commit()

        # 生成一个简单的 Token (生产环境建议用 JWT)
        token = secrets.token_hex(16)

        return jsonify({
            "code": 200,
            "msg": "登录成功",
            "data": {
                "uid": user.id,
                "nickname": user.nickname,
                "avatar_url": user.avatar_url,
                "token": token
            }
        }), 200

    else:
        return jsonify({"code": 401, "msg": "手机号或密码错误"}), 200


