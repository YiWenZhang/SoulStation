from flask import Blueprint, jsonify, request, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import secrets
from ..extensions import db
import json
from sqlalchemy import desc, null
from sqlalchemy.orm.attributes import flag_modified # 用于强制更新JSON字段
from ..utils.common import generate_report_markdown, get_dimension_description, get_overall_risk_comment
from ..models import AssessmentRule
from ..utils.common import calculate_scl90_level, get_risk_suggestion
from ..models import AssessmentRule, AssessmentReport  # 确保引入模型
from ..models import User, AssessmentSession, AssessmentReport, Question, QuestionOption, QuestionCategory, AssessmentRule, AIConsultation

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


    # 3. 构造返回
    return jsonify({
        "code": 200,
        "msg": "获取成功",
        "data": {
            "user_info": {
                "nickname": user.nickname,
                "avatar_url": user.avatar_url
            },
            "tracking_reminder": reminder_data,
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
        # 【安全补丁】如果发现这个ongoing会话其实已经有报告了（即实际上已完成），
        # 应该视为已完成，不返回resumed，而是直接跳到下面去开新的。
        if ongoing_session.report:
            ongoing_session.status = 'completed'
            db.session.commit()
            ongoing_session = None # 重置变量，让逻辑往下走去创建新的
        else:
            # 真正的未完成存档
            history = ongoing_session.chat_history
            if isinstance(history, list):
                history = {}

            return jsonify({
                "code": 200,
                "msg": "发现未完成的测评",
                "data": {
                    "session_id": ongoing_session.id,
                    "status": "ongoing",
                    "is_resumed": True,
                    "current_progress_index": ongoing_session.current_step,
                    "answers_snapshot": history
                }
            })

    # 3. 否则（action='new' 或 无存档），创建新会话
    total_count = Question.query.filter_by(is_enabled=True).count()

    # 【修改逻辑】如果有旧的未完成会话，将其删除
    if ongoing_session:
        # 如果用户选择开启新的(action='new')，说明不要旧进度了，直接删除
        db.session.delete(ongoing_session)
        # 注意：这里不需要 commit，下面添加新会话时一起 commit 即可

    new_session = AssessmentSession(
        user_id=uid,
        mode='questionnaire',
        status='ongoing',
        total_steps=total_count,
        current_step=0,
        chat_history={}
    )

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
# 7. 测评流程：提交保存结果
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
        return jsonify({"code": 400, "msg": "没有答题数据"}), 400

    # 2. 完整性校验
    total_questions_count = Question.query.filter_by(is_enabled=True).count()
    if len(answers) < total_questions_count:
        missing_count = total_questions_count - len(answers)
        return jsonify({
            "code": 400,
            "msg": f"还有 {missing_count} 道题目未完成",
            "data": {"total": total_questions_count, "answered": len(answers)}
        }), 400

    # ======================================================
    # 核心逻辑：只计算数值，不生成文案
    # ======================================================

    # A. 准备基础数据
    # 获取涉及的题目信息
    questions = Question.query.filter(Question.id.in_(map(int, answers.keys()))).all()
    # 获取分类映射表: {id: "焦虑"}
    categories = {c.id: c.name for c in QuestionCategory.query.all()}

    # B. 维度算分 (SCL-90 因子分)
    dimension_scores = {}  # 临时桶: {"焦虑": [2, 3, 4]}

    for q in questions:
        # 容错处理：确保分数是 float
        try:
            score = float(answers.get(str(q.id), 0))
        except (ValueError, TypeError):
            continue

        cat_name = categories.get(q.category_id, "其他")

        if cat_name not in dimension_scores:
            dimension_scores[cat_name] = []
        dimension_scores[cat_name].append(score)

    # C. 生成雷达图数据 & 筛选高风险维度
    radar_data = {}  # 存库用：{"焦虑": 2.5, "抑郁": 1.2}
    high_risk_dims = []  # 存库用：["焦虑", "强迫"]

    for dim, scores_list in dimension_scores.items():
        if not scores_list: continue
        # 因子分 = 总分 / 题目数
        avg_score = round(sum(scores_list) / len(scores_list), 2)
        radar_data[dim] = avg_score

        # 判定风险：因子分 >= 3
        if avg_score >= 3.0:
            high_risk_dims.append(dim)

    # D. 计算全局总分
    valid_scores_list = [float(v) for v in answers.values() if str(v).replace('.', '', 1).isdigit()]
    total_score = sum(valid_scores_list) if valid_scores_list else 0
    total_avg = round(total_score / len(valid_scores_list), 2) if valid_scores_list else 0

    # E. 判定总体风险等级 (业务规则)
    risk_level = 'good'
    if len(high_risk_dims) >= 5:  # 3个以上维度异常 -> 严重
        risk_level = 'severe'
    elif len(high_risk_dims) >= 2:  # 任意维度异常 -> 中度
        risk_level = 'moderate'

    # F. 生成极简摘要 (仅作列表展示用，非报告正文)
    summary_short = "心理状态良好"
    if risk_level != 'good':
        summary_short = f"{len(high_risk_dims)}个维度存在风险倾向"

    # ======================================================
    # 存库：只存干货
    # ======================================================
    try:
        report = AssessmentReport(
            session_id=session.id,

            # 1. 核心数值
            radar_data=radar_data,  # JSON: 每个维度的具体得分
            total_score=total_score,  # Float: 卷面总分
            total_avg=total_avg,  # Float: 总均分

            # 2. 核心结论
            risk_level=risk_level,  # String: good/moderate/severe
            high_risk_dimensions=high_risk_dims,  # JSON List: ["焦虑", ...]
            summary_short=summary_short,  # String: 列表页显示的短句

            # 3. 留空字段 (不再生成)
            # detail_content_md=""  # 设为空字符串或 None
        )
        session.status = 'completed'
        db.session.add(report)
        db.session.add(session)
        db.session.commit()

        return jsonify({
            "code": 200,
            "msg": "提交成功",
            "data": {
                "report_id": report.id,
                "risk_level": risk_level  # 方便前端做简单的即时反馈
            }
        })

    except Exception as e:
        db.session.rollback()
        # 打印详细堆栈方便调试，生产环境可记录日志
        print(f"Report Save Error: {e}")
        return jsonify({"code": 500, "msg": "生成报告失败，请重试"}), 500


# ==========================================
# 8. 获取报告详情接口
# ==========================================
@api_bp.route('/assessment/report/detail', methods=['GET'])
def get_report_detail():
    report_id = request.args.get('report_id')
    uid = request.args.get('uid')

    # 1. 基础校验
    if not report_id or not uid:
        return jsonify({"code": 400, "msg": "参数缺失"}), 400

    report = AssessmentReport.query.get(report_id)
    if not report:
        return jsonify({"code": 404, "msg": "报告不存在"}), 404

    # 权限校验 (确保只能看自己的)
    if str(report.session.user_id) != str(uid):
        return jsonify({"code": 403, "msg": "无权查看此报告"}), 403

    # =================================================
    # 核心逻辑：动态拼装数据
    # =================================================

    # A. 准备标准顺序 (确保前端展示顺序固定，而不是乱序)
    std_dimensions = [
        "躯体化", "强迫症状", "人际关系敏感", "抑郁", "焦虑",
        "敌对", "恐怖", "偏执", "精神病性", "其他"
    ]

    # B. 预加载所有规则 (一次性查库，性能最优)
    #    将规则转化为字典方便查找: rules_map["焦虑"][3] = {label, desc}
    all_rules = AssessmentRule.query.all()
    rules_map = {}
    for r in all_rules:
        if r.dimension_name not in rules_map:
            rules_map[r.dimension_name] = {}
        rules_map[r.dimension_name][r.level] = {
            "label": r.level_label,
            "desc": r.description
        }

    # C. 遍历维度，生成详细列表 + 拼接 Markdown
    dimensions_detail_list = []

    # 这里的 radar_data 是接口7存进去的纯数字: {"焦虑": 2.5, ...}
    current_radar = report.radar_data or {}

    # 开始拼接 Markdown 头部
    md_content = f"### 📊 测评结果综述\n\n"
    md_content += f"本次测评总分 **{report.total_score}**，平均分 **{report.total_avg}**。\n\n"
    md_content += f"> {get_risk_suggestion(report.risk_level)}\n\n"
    md_content += "---\n\n### 🧩 维度详细分析\n\n"

    for dim_name in std_dimensions:
        # 1. 获取分数 (如果没分，默认为1.0)
        score = current_radar.get(dim_name, 1.0)

        # 2. 计算等级 (调用 utils 新函数)
        level_int = calculate_scl90_level(score)

        # 3. 查找文案 (核心步骤)
        #    如果数据库里没有配"其他"维度的规则，做一个兜底
        dim_key = dim_name if dim_name in rules_map else "其他"

        #    获取对应等级的规则，如果没有配，给个默认值
        rule_info = rules_map.get(dim_key, {}).get(level_int, {
            "label": "正常",
            "desc": "当前维度未检测到明显异常。"
        })

        # 4. 加入列表 (给前端画列表用)
        dimensions_detail_list.append({
            "name": dim_name,
            "score": score,
            "level": rule_info['label'],  # 例如： "中度"
            "level_int": level_int,  # 例如： 3
            "description": rule_info['desc']  # 例如： "您可能感到明显的..."
        })

        # 5. 拼接到 Markdown (给前端展示大段文字用)
        #    只展示有一定风险的维度，或者全部展示，取决于你想给用户看多少
        #    这里策略是：只展示 >= 2级 (轻度以上) 的维度，避免报告太长
        if level_int >= 2:
            md_content += f"#### **{dim_name}** ({rule_info['label']})\n"
            md_content += f"* **指数**: {score}\n"
            md_content += f"* **分析**: {rule_info['desc']}\n\n"

    # 如果所有维度都很好，加一句收尾
    if report.risk_level == 'good':
        md_content += "各项指标均在正常范围内，未发现明显心理困扰。\n"

    md_content += "\n> *注：本报告基于SCL-90常模数据生成，结果仅供参考，不作为临床诊断依据。*"

    # =================================================
    # 构造返回结构
    # =================================================
    return jsonify({
        "code": 200,
        "msg": "获取成功",
        "data": {
            # 1. 基础信息
            "base_info": {
                "report_no": f"RPT-{report.id}",
                "date": report.generated_at.strftime('%Y-%m-%d'),
                "user_name": report.session.user.nickname,
                "mode_name": "SCL-90 专业量表测评"
            },

            # 2. 核心结论 (直接读库)
            "core_result": {
                "risk_level": report.risk_level,
                "summary_label": report.summary_short,
                "total_score": int(report.total_score or 0),
                "total_avg": report.total_avg or 0,
                "overall_advice": get_risk_suggestion(report.risk_level)
            },

            # 3. 图表数据 (前端可以直接用)
            "charts": {
                "radar_data": [
                    {"name": k, "value": v, "fullMark": 5}
                    for k, v in current_radar.items()
                ]
            },

            # 4. 详细列表 (用于前端渲染卡片或表格)
            "dimensions_detail": dimensions_detail_list,

            # 5. 完整文案 (刚刚动态生成的 Markdown)
            "content": {
                "advice_md": md_content
            },

            "actions": {"can_chat": True, "can_download": True}
        }
    })

# ==========================================
# 9. 历史测评数据获取接口
# ==========================================
# 9.1 获取层级历史记录列表 (用于“历史记录”页面)
# 结构：返回所有已完成的报告，每份报告下包含其所有的 AI 问诊记录
@api_bp.route('/history/list', methods=['GET'])
def get_history_list():
    uid = request.args.get('uid')
    if not uid:
        return jsonify({'code': 400, 'msg': '参数缺失: uid'}), 400

    try:
        # 1. 查出该用户所有已完成的测评会话 (按最后更新时间倒序)
        sessions = AssessmentSession.query.filter_by(
            user_id=uid,
            status='completed'
        ).order_by(desc(AssessmentSession.updated_at)).all()

        result_list = []

        for session in sessions:
            report = session.report
            if not report:
                continue

            # 2. 查出该报告关联的所有 AI 问诊记录 (按次序倒序，最新的在上面)
            # 使用模型中定义的 consultations 关系
            consultations = report.consultations.order_by(desc(AIConsultation.sequence_number)).all()

            consultation_list_data = []
            for cons in consultations:
                consultation_list_data.append({
                    "id": cons.id,
                    "sequence_number": cons.sequence_number,  # 第几次问诊
                    "date": cons.updated_at.strftime('%Y-%m-%d %H:%M'),  # 问诊时间
                    # 简短摘要，用于列表展示，如果没有诊断书说明还在进行中
                    "summary_snippet": (
                                cons.diagnosis_summary[:40] + '...') if cons.diagnosis_summary else "问诊进行中...",
                    "status": "completed" if cons.diagnosis_summary else "ongoing"
                })

            # 3. 组装父级（测评报告）数据
            result_list.append({
                "report_id": report.id,
                "report_date": report.generated_at.strftime('%Y-%m-%d'),
                "mode": session.mode,  # 用于前端区分图标
                "mode_name": "AI对话测评" if session.mode == 'ai_chat' else "专业量表测评",
                "risk_level": report.risk_level,  # good/moderate/severe
                "summary": report.summary_short,  # 报告的主结论
                "total_score": report.total_score,  # 显示分数

                # --- 核心：这里嵌套了该报告下的所有问诊记录 ---
                "consultations": consultation_list_data
            })

        return jsonify({
            "code": 200,
            "msg": "获取历史记录成功",
            "data": result_list
        })

    except Exception as e:
        print(f"Error getting history: {e}")
        return jsonify({'code': 500, 'msg': '获取历史记录失败'}), 500


# 9.2 获取单次 AI 问诊的详情 (用于点击“记录x”时查看)
@api_bp.route('/history/consultation/detail', methods=['GET'])
def get_consultation_detail_in_api():
    consultation_id = request.args.get('id')
    if not consultation_id:
        return jsonify({'code': 400, 'msg': '参数缺失: id'}), 400

    try:
        cons = AIConsultation.query.get(consultation_id)
        if not cons:
            return jsonify({'code': 404, 'msg': '未找到该问诊记录'}), 404

        return jsonify({
            "code": 200,
            "msg": "获取成功",
            "data": {
                "id": cons.id,
                "report_id": cons.report_id,
                "sequence_number": cons.sequence_number,
                "date": cons.updated_at.strftime('%Y-%m-%d %H:%M'),
                "chat_history": cons.chat_history,  # 完整的对话记录
                "diagnosis_report": cons.diagnosis_summary  # 完整的 AI 诊断书
            }
        })

    except Exception as e:
        print(f"Error getting detail: {e}")
        return jsonify({'code': 500, 'msg': '获取详情失败'}), 500



# ==========================================
# 10. 个人主页修改
# ==========================================
import os
from flask import request, jsonify, current_app, url_for
from werkzeug.utils import secure_filename
from src.extensions import db
from src.models import User
import uuid


# --- 辅助函数：检查文件扩展名 ---
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


# --- 1. 修改用户基本信息 (昵称) ---
@api_bp.route('/user/profile', methods=['POST'])
def update_profile():
    # 假设前端传递的是 JSON: { "uid": 1, "nickname": "新名字" }
    # 实际项目中应该从 Token 获取 uid，这里为了保持你现有的风格，从参数获取
    data = request.get_json()
    uid = data.get('uid')
    nickname = data.get('nickname')

    if not uid or not nickname:
        return jsonify({'code': 400, 'msg': '参数缺失'}), 400

    user = User.query.get(uid)
    if not user:
        return jsonify({'code': 404, 'msg': '用户不存在'}), 404

    try:
        user.nickname = nickname
        db.session.commit()
        return jsonify({
            'code': 200,
            'msg': '修改成功',
            'data': {
                'nickname': user.nickname
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'msg': str(e)}), 500


# --- 2. 上传头像 ---
@api_bp.route('/user/avatar', methods=['POST'])
def upload_avatar():
    # 前端需要使用 FormData 发送数据，字段名为 'file'，同时附带 'uid'
    if 'file' not in request.files:
        return jsonify({'code': 400, 'msg': '未找到文件'}), 400

    file = request.files['file']
    uid = request.form.get('uid')

    if not uid:
        return jsonify({'code': 400, 'msg': '缺少用户ID'}), 400

    if file.filename == '':
        return jsonify({'code': 400, 'msg': '文件名为空'}), 400

    if file and allowed_file(file.filename):
        try:
            # 1. 生成安全的文件名 (使用 UUID 防止重名)
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"user_{uid}_{uuid.uuid4().hex[:8]}.{ext}"

            # 2. 确保目录存在
            upload_path = current_app.config['UPLOAD_FOLDER']
            if not os.path.exists(upload_path):
                os.makedirs(upload_path)

            # 3. 保存文件
            file_path = os.path.join(upload_path, filename)
            file.save(file_path)

            # 4. 生成可访问的 URL
            # 假设后端运行在 5000 端口，静态文件路径为 /static/avatars/...
            # 这里的 URL 需要根据你的实际部署域名调整，本地开发通常是相对路径或完整路径
            avatar_url = f"/static/avatars/{filename}"

            # 5. 更新数据库
            user = User.query.get(uid)
            if user:
                user.avatar_url = avatar_url
                db.session.commit()

            return jsonify({
                'code': 200,
                'msg': '头像上传成功',
                'data': {
                    'avatar_url': avatar_url
                }
            })

        except Exception as e:
            print(e)
            return jsonify({'code': 500, 'msg': '上传处理失败'}), 500

    return jsonify({'code': 400, 'msg': '不支持的文件格式'}), 400