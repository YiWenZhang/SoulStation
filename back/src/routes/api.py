from flask import Blueprint, jsonify, request, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import secrets
from ..extensions import db
from ..models import User, AssessmentSession, AssessmentReport
from sqlalchemy import desc

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/test', methods=['GET'])
def test_api():
    return jsonify({
        "code": 200,
        "msg": "后端环境连接成功！",
        "data": None
    })


# ==========================================
# 1. 注册接口 (Register) - 支持管理员认证
# ==========================================
@api_bp.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"code": 400, "msg": "请提供注册信息"}), 400

    phone = data.get('phone')
    password = data.get('password')
    # 获取角色，默认为普通用户 'user'
    role = data.get('role', 'user')
    # 获取管理员密钥 (仅当 role 为 admin 时需要)
    admin_key = data.get('admin_key')

    nickname = data.get('nickname', f"用户{phone[-4:]}") if phone else "新用户"

    # 1. 基础参数校验
    if not phone or not password:
        return jsonify({"code": 400, "msg": "手机号和密码不能为空"}), 400

    if role not in ['user', 'admin']:
        return jsonify({"code": 400, "msg": "无效的用户角色"}), 400

    # 2. 【核心修改】管理员身份校验
    if role == 'admin':
        # 从配置中读取预设的密钥
        required_key = current_app.config.get('ADMIN_SECRET_KEY')
        if not admin_key or admin_key != required_key:
            return jsonify({"code": 403, "msg": "管理员密钥错误，无法注册为管理员"}), 403

        # 管理员默认昵称处理
        if not data.get('nickname'):
            nickname = f"管理员{phone[-4:]}"

    # 3. 检查手机号是否已存在
    if User.query.filter_by(phone=phone).first():
        return jsonify({"code": 400, "msg": "该手机号已注册，请直接登录"}), 400

    # 4. 创建新用户
    try:
        new_user = User(
            phone=phone,
            nickname=nickname,
            password_hash=generate_password_hash(password),
            role=role,  # === 【新增】写入角色 ===
            avatar_url="https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png"
        )

        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            "code": 200,
            "msg": f"{'管理员' if role == 'admin' else '用户'}注册成功，请登录"
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "msg": f"注册失败: {str(e)}"}), 500


# ==========================================
# 2. 登录接口 (Login) - 返回用户角色
# ==========================================
@api_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    phone = data.get('phone')
    password = data.get('password')

    if not phone or not password:
        return jsonify({"code": 400, "msg": "请输入账号密码"}), 400

    user = User.query.filter_by(phone=phone).first()

    if user and check_password_hash(user.password_hash, password):
        user.last_login_at = datetime.utcnow()
        db.session.commit()

        token = secrets.token_hex(16)

        return jsonify({
            "code": 200,
            "msg": "登录成功",
            "data": {
                "uid": user.id,
                "nickname": user.nickname,
                "avatar_url": user.avatar_url,
                "role": user.role,  # === 【新增】返回角色，前端据此跳转 ===
                "token": token
            }
        }), 200

    else:
        return jsonify({"code": 401, "msg": "手机号或密码错误"}), 200


# ==========================================
# 3. 首页数据接口 (Home Dashboard)
# ==========================================
@api_bp.route('/home/index', methods=['GET'])
def home_index():
    # 1. 获取并校验参数 (严格限制为已登录用户)
    uid = request.args.get('uid')
    if not uid:
        return jsonify({"code": 401, "msg": "未登录，请先登录"}), 401

    user = User.query.get(uid)
    if not user:
        return jsonify({"code": 404, "msg": "用户不存在"}), 404

    # 2. 核心数据一：改善追踪提醒
    # 逻辑：距离上次测评超过 30 天则提示
    reminder_data = {"show": False, "message": ""}

    if user.last_assessment_at:
        days_diff = (datetime.utcnow() - user.last_assessment_at).days
        if days_diff >= 30:
            reminder_data = {
                "show": True,
                "message": f"距离上次测评已过 {days_diff} 天，建议进行复测以追踪改善情况。"
            }

    # 3. 核心数据二：历史记录
    # 获取用户已完成('completed')的最近记录
    history_list = []
    recent_sessions = AssessmentSession.query.filter_by(
        user_id=uid,
        status='completed'
    ).order_by(desc(AssessmentSession.updated_at)).limit(3).all()  # 限制返回最近3条

    for session in recent_sessions:
        if session.report:
            history_list.append({
                "id": session.report.id,
                "date": session.report.generated_at.strftime('%Y-%m-%d'),
                "mode": session.mode,
                "risk_level": session.report.risk_level,
                "summary": session.report.summary_short
            })

    # 4. 构造返回
    return jsonify({
        "code": 200,
        "msg": "获取成功",
        "data": {
            "user_info": {
                "nickname": user.nickname,
                "avatar_url": user.avatar_url
            },
            "tracking_reminder": reminder_data,
            "history_records": history_list
        }
    })