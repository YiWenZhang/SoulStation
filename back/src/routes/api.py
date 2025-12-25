from flask import Blueprint, jsonify, request, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import secrets
from ..extensions import db
import json
from ..models import User, AssessmentSession, AssessmentReport, Question, QuestionOption, QuestionCategory
from sqlalchemy import desc, null
from sqlalchemy.orm.attributes import flag_modified # 用于强制更新JSON字段
from ..utils.common import generate_report_markdown

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/test', methods=['GET'])
def test_api():
    return jsonify({
        "code": 200,
        "msg": "后端环境连接成功！",
        "data": None
    })


# ==========================================
# 配置项：管理员注册密钥 (硬编码字符串)
# ==========================================
ADMIN_SECRET_KEY = "SoulStation2025_Admin"


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
    # 获取前端传来的密钥 (仅当 role 为 admin 时需要)
    input_admin_key = data.get('admin_key')
    # ========================================================
    # 1.5 【新增】详细格式校验 (密码长度、手机号格式)
    # ========================================================

    # 校验 A: 密码长度 (例如：不能少于 6 位)
    if len(password) < 6:
        return jsonify({"code": 400, "msg": "密码长度不能少于6位"}), 400

    # 校验 B: 密码长度 (例如：不能超过 20 位)
    if len(password) > 20:
        return jsonify({"code": 400, "msg": "密码长度不能超过20位"}), 400

    # 校验 C: 手机号格式 (简单的 11 位数字校验)
    if len(phone) != 11 or not phone.isdigit():
        return jsonify({"code": 400, "msg": "请输入有效的11位手机号码"}), 400

    # ========================================================
    # 1. 基础参数校验
    if not phone or not password:
        return jsonify({"code": 400, "msg": "手机号和密码不能为空"}), 400

    if role not in ['user', 'admin']:
        return jsonify({"code": 400, "msg": "无效的用户角色"}), 400

    # 2. 【核心逻辑】管理员身份校验
    nickname = data.get('nickname', f"用户{phone[-4:]}")

    if role == 'admin':
        # 校验密钥：如果不匹配，直接拒绝
        if not input_admin_key or input_admin_key != ADMIN_SECRET_KEY:
            # 对应文档：code: 403, msg: "管理员密钥错误"
            return jsonify({"code": 403, "msg": "管理员密钥错误，无法注册"}), 403

        # 如果是管理员，且没填昵称，给个特殊的默认昵称
        if not data.get('nickname'):
            nickname = f"管理员{phone[-4:]}"

    # 3. 检查手机号是否已存在
    if User.query.filter_by(phone=phone).first():
        # 对应文档：code: 400, msg: "该手机号已注册"
        return jsonify({"code": 400, "msg": "该手机号已注册，请直接登录"}), 400

    # 4. 创建新用户
    try:
        new_user = User(
            phone=phone,
            nickname=nickname,
            password_hash=generate_password_hash(password),
            role=role,  # === 关键：写入 user 或 admin ===
            avatar_url="https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png"
        )

        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            "code": 200,
            "msg": f"{'管理员' if role == 'admin' else '用户'}注册成功，请登录",
            "data": None
        }), 200

    except Exception as e:
        db.session.rollback()
        # 服务器内部错误，返回 500
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

    # 验证密码
    if user and check_password_hash(user.password_hash, password):
        # 更新最后登录时间
        user.last_login_at = datetime.utcnow()
        db.session.commit()

        # 生成 Token (这里是简化版，实际项目建议用 JWT)
        token = secrets.token_hex(16)

        # 对应文档：返回 role 字段
        return jsonify({
            "code": 200,
            "msg": "登录成功",
            "data": {
                "uid": user.id,
                "nickname": user.nickname,
                "avatar_url": user.avatar_url,
                "role": user.role,  # === 关键：前端根据这个跳转 ===
                "token": token
            }
        }), 200

    else:
        # 对应文档：code: 401, msg: "账号或密码错误"
        # 【修正】：这里 HTTP 状态码也改为 401，与 JSON code 保持一致
        return jsonify({"code": 401, "msg": "账号或密码错误"}), 401


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


# ==========================================
# 4. 测评流程：初始化/检查状态
# ==========================================
@api_bp.route('/assessment/questionnaire/start', methods=['POST'])
def start_questionnaire():
    data = request.get_json()
    uid = data.get('uid')
    action = data.get('action', 'check')  # 'check' or 'new'

    if not uid:
        return jsonify({"code": 401, "msg": "未登录"}), 401

    # 1. 查找是否有未完成的题库测评
    ongoing_session = AssessmentSession.query.filter_by(
        user_id=uid,
        mode='questionnaire',
        status='ongoing'
    ).order_by(desc(AssessmentSession.updated_at)).first()

    # 2. 如果是检查模式，且有存档，直接返回存档信息
    if action == 'check' and ongoing_session:
        # 处理历史数据格式兼容（防止之前存的是list）
        history = ongoing_session.chat_history
        if isinstance(history, list):
            history = {}

        return jsonify({
            "code": 200,
            "msg": "发现未完成的测评",
            "data": {
                "session_id": ongoing_session.id,
                "status": "ongoing",
                "is_resumed": True,  # 告诉前端这是存档
                "current_progress_index": ongoing_session.current_step,
                "answers_snapshot": history  # 前端拿到这个回显答案
            }
        })

    # 3. 否则（action='new' 或 无存档），创建新会话
    # 先获取题目总数，用于设置 total_steps
    total_count = Question.query.filter_by(is_enabled=True).count()

    new_session = AssessmentSession(
        user_id=uid,
        mode='questionnaire',
        status='ongoing',
        total_steps=total_count,
        current_step=0,
        chat_history={}  # 初始化为空字典
    )

    # 如果有旧的ongoing，可以考虑将其关闭（可选逻辑），这里简单处理直接开新的
    if ongoing_session:
        ongoing_session.status = 'abandoned'  # 标记废弃

    db.session.add(new_session)
    db.session.commit()

    return jsonify({
        "code": 200,
        "msg": "开启新测评",
        "data": {
            "session_id": new_session.id,
            "status": "ongoing",
            "is_resumed": False,
            "current_progress_index": 0,
            "answers_snapshot": {}
        }
    })


# ==========================================
# 5. 测评流程：获取题目数据
# ==========================================
@api_bp.route('/assessment/questionnaire/questions', methods=['GET'])
def get_questions():
    # 获取所有启用的题目，按ID排序 (或按数据库中的 sort_order 排序)
    questions = Question.query.filter_by(is_enabled=True).order_by(Question.id).all()

    result = []
    for q in questions:
        # 组装选项
        options_data = []
        # 注意：这里需要确保 options 按照分数或顺序排列
        sorted_options = sorted(q.options, key=lambda x: x.score)
        for opt in sorted_options:
            options_data.append({
                "id": opt.id,
                "label": opt.label,
                "score": opt.score
            })

        result.append({
            "id": q.id,
            "stem": q.stem,
            "type": q.type,
            "options": options_data
        })

    return jsonify({
        "code": 200,
        "msg": "获取成功",
        "data": {
            "questions": result
        }
    })


# ==========================================
# 6. 测评流程：保存进度 (心跳/切换题目时调用)
# ==========================================
@api_bp.route('/assessment/questionnaire/save', methods=['POST'])
def save_progress():
    data = request.get_json()
    session_id = data.get('session_id')
    current_index = data.get('current_index')  # 当前停留在第几题
    new_answers = data.get('answers')  # e.g. {"1": 2, "5": 3} 增量或全量均可

    if not session_id:
        return jsonify({"code": 400, "msg": "参数错误"}), 400

    session = AssessmentSession.query.get(session_id)
    if not session or session.status != 'ongoing':
        return jsonify({"code": 400, "msg": "会话无效或已结束"}), 400

    # 1. 更新进度指针
    if current_index is not None:
        session.current_step = current_index

    # 2. 更新答案数据
    if new_answers:
        # 确保是字典
        history = session.chat_history
        if not history or isinstance(history, list):
            history = {}

        # 合并新答案 (Key为题目ID字符串，Value为分数)
        # 注意：前端传来的Key可能是数字，建议统一转字符串处理，或者保持原样
        for k, v in new_answers.items():
            history[str(k)] = v

        session.chat_history = history
        # SQLAlchemy中修改JSON字段有时需要显式标记
        flag_modified(session, "chat_history")

    session.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({"code": 200, "msg": "进度已保存"})


# ==========================================
# 7. 测评流程：提交并生成报告
# ==========================================
@api_bp.route('/assessment/questionnaire/submit', methods=['POST'])
def submit_assessment():
    data = request.get_json()
    session_id = data.get('session_id')

    session = AssessmentSession.query.get(session_id)
    if not session:
        return jsonify({"code": 404, "msg": "会话不存在"}), 404

    # 1. 获取用户所有答案
    answers = session.chat_history  # {"qid": score, ...}
    if not isinstance(answers, dict) or not answers:
        return jsonify({"code": 400, "msg": "没有答题数据，无法提交"}), 400

    # ======================================================
    # 【新增逻辑】 2. 完整性校验：检查是否答完了所有题目
    # ======================================================
    # 获取当前启用题目的总数
    total_questions_count = Question.query.filter_by(is_enabled=True).count()

    # 也就是检查提交的答案数量是否等于题目总数
    # (注意：answers 的 key 是题目ID，数量即为已答题数)
    if len(answers) < total_questions_count:
        missing_count = total_questions_count - len(answers)
        return jsonify({
            "code": 400,
            "msg": f"还有 {missing_count} 道题目未完成，请继续作答",
            "data": {
                "total": total_questions_count,
                "answered": len(answers)
            }
        }), 400
    # ======================================================

    # 3. SCL-90 算分逻辑
    #    需要查询所有题目对应的维度 (Category)
    #    这里做一个批量查询优化，把题目ID映射到 Category Name

    # 获取所有题目及其分类名称
    # 假设 Question.category_id 关联 QuestionCategory.id
    questions = Question.query.filter(Question.id.in_(map(int, answers.keys()))).all()

    # 准备数据桶： { "焦虑": [2, 3, 1], "抑郁": [4, 5] }
    dimension_scores = {}

    # 预先获取所有分类映射 (id -> name)
    categories = {c.id: c.name for c in QuestionCategory.query.all()}

    for q in questions:
        # 获取该题得分
        score = answers.get(str(q.id))
        if score is None: continue

        # 获取维度名
        cat_name = categories.get(q.category_id, "其他")

        if cat_name not in dimension_scores:
            dimension_scores[cat_name] = []
        dimension_scores[cat_name].append(score)

    # 3. 计算因子分 (均分)
    #    SCL-90 规则：因子分 = 该维度总分 / 该维度题目数
    radar_data = {}
    high_risk_dims = []

    for dim, scores_list in dimension_scores.items():
        if not scores_list: continue
        avg_score = sum(scores_list) / len(scores_list)
        radar_data[dim] = round(avg_score, 2)

        # 简单判定：因子分 >= 2 (或2.5) 为阳性/风险
        if avg_score >= 2.0:
            high_risk_dims.append(dim)

    # 4. 判定总体风险等级
    #    SCL-90通常看：总分、阳性项目数、或者因子分。这里简化用因子分判定。
    risk_level = 'good'
    if len(high_risk_dims) >= 3:
        risk_level = 'severe'  # 严重：多个维度异常
    elif len(high_risk_dims) > 0:
        risk_level = 'moderate'  # 中度：有维度异常
    else:
        risk_level = 'good'  # 良好

    # 生成简单的结论文本
    summary_short = "心理状态良好"
    if risk_level != 'good':
        summary_short = f"在 {', '.join(high_risk_dims[:3])} 等方面存在一定心理压力"

    # ========================================================
    # 【核心修改】：调用 common 生成 Markdown
    # ========================================================
    detail_content_md = generate_report_markdown(radar_data, risk_level, high_risk_dims)

    # 5. 保存报告
    try:
        report = AssessmentReport(
            session_id=session.id,
            summary_short=summary_short,
            detail_content_md=detail_content_md,
            radar_data=radar_data,
            risk_level=risk_level,
            high_risk_dimensions=high_risk_dims
        )

        session.status = 'completed'
        session.updated_at = datetime.utcnow()
        # 更新用户最后测评时间
        user = User.query.get(session.user_id)
        if user:
            user.last_assessment_at = datetime.utcnow()

        db.session.add(report)
        db.session.commit()

        return jsonify({
            "code": 200,
            "msg": "报告生成成功",
            "data": {"report_id": report.id}
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "msg": f"生成报告失败: {str(e)}"}), 500


# ==========================================
# 8. 获取报告详情 (PRD 3.1.5 核心接口) [New]
# ==========================================
@api_bp.route('/assessment/report/detail', methods=['GET'])
def get_report_detail():
    report_id = request.args.get('report_id')
    uid = request.args.get('uid')

    if not report_id or not uid:
        return jsonify({"code": 400, "msg": "参数缺失"}), 400

    report = AssessmentReport.query.get(report_id)
    if not report:
        return jsonify({"code": 404, "msg": "报告不存在"}), 404

    # 权限校验
    if str(report.session.user_id) != str(uid):
        return jsonify({"code": 403, "msg": "无权查看此报告"}), 403

    user = report.session.user

    # 组装图表数据 (适配前端图表组件格式)
    chart_data = []
    for dim, val in report.radar_data.items():
        chart_data.append({
            "name": dim,
            "value": val,
            "fullMark": 5
        })

    # 风险颜色映射
    color_map = {
        "good": "green",
        "mild": "yellow",
        "moderate": "orange",
        "severe": "red"
    }

    return jsonify({
        "code": 200,
        "msg": "获取成功",
        "data": {
            "base_info": {
                "report_no": f"RPT-{report.id}",
                "date": report.generated_at.strftime('%Y-%m-%d'),
                "user_name": user.nickname,
                "mode_name": "SCL-90 专业量表测评"
            },
            "core_result": {
                "risk_level": report.risk_level,
                "risk_color": color_map.get(report.risk_level, "green"),
                "summary_label": report.summary_short,
                "score_interpretation": "SCL-90采用1-5分评分制，分数越高代表症状越明显。≥2分提示存在轻度症状。"
            },
            "charts": {
                "radar_data": chart_data
            },
            "content": {
                # 直接返回数据库中已生成好的 Markdown
                "advice_md": report.detail_content_md
            },
            "actions": {
                "can_chat": True,
                "can_download": True
            }
        }
    })