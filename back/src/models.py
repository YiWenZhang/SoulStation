from .extensions import db
from datetime import datetime
from sqlalchemy.dialects.mysql import JSON, MEDIUMTEXT


# ==========================================
# 1. 用户与权限模块
# ==========================================

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    # 登录凭证
    phone = db.Column(db.String(20), unique=True, index=True)
    email = db.Column(db.String(100), unique=True)  # PRD提到支持邮箱 [cite: 761]
    password_hash = db.Column(db.String(255))

    # 用户画像
    nickname = db.Column(db.String(50))
    avatar_url = db.Column(db.String(255))

    # 权限控制 [cite: 758]
    # role: 'user' (普通用户), 'admin' (管理员)
    role = db.Column(db.String(20), default='user', index=True)

    # 状态
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login_at = db.Column(db.DateTime)

    # 关系
    sessions = db.relationship('AssessmentSession', backref='user', lazy='dynamic')
    feedbacks = db.relationship('UserFeedback', backref='user', lazy='dynamic')


# ==========================================
# 2. 核心业务模块 (测评会话与报告)
# ==========================================

class AssessmentSession(db.Model):
    __tablename__ = 'assessment_sessions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # 测评方式区分 [cite: 731]
    # mode: 'ai_chat' (AI对话), 'questionnaire' (题库答题)
    mode = db.Column(db.String(20), default='ai_chat')

    status = db.Column(db.String(20), default='ongoing', comment='ongoing, completed')
    current_step = db.Column(db.Integer, default=0)
    total_steps = db.Column(db.Integer, default=10)

    # 核心：存储对话历史 (JSON)
    chat_history = db.Column(JSON, default=list)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    report = db.relationship('AssessmentReport', backref='session', uselist=False)


class AssessmentReport(db.Model):
    __tablename__ = 'assessment_reports'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('assessment_sessions.id'), unique=True, nullable=False)

    # 报告核心展示
    summary_short = db.Column(db.String(255), comment='综合心理状态标签')
    detail_content_md = db.Column(MEDIUMTEXT, comment='Markdown详情')
    radar_data = db.Column(JSON, comment='雷达图数据')

    # 数据管理页所需的筛选字段
    # risk_level: 'good', 'mild', 'moderate', 'severe'
    risk_level = db.Column(db.String(20), index=True, comment='风险等级')

    # 存储高风险维度列表，如 ["anxiety", "depression"]，用于高级搜索
    high_risk_dimensions = db.Column(JSON, comment='核心高风险维度')

    generated_at = db.Column(db.DateTime, default=datetime.utcnow)


# ==========================================
# 3. 后台页面1：题库管理模块 [cite: 925]
# ==========================================

class QuestionCategory(db.Model):
    """题目分类树 (SCL90维度) [cite: 928]"""
    __tablename__ = 'question_categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # 如：躯体化、焦虑
    parent_id = db.Column(db.Integer, db.ForeignKey('question_categories.id'), nullable=True)

    children = db.relationship('QuestionCategory', backref=db.backref('parent', remote_side=[id]))


class Question(db.Model):
    """题库题目 [cite: 932]"""
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    stem = db.Column(db.Text, nullable=False, comment='题干')
    type = db.Column(db.String(20), default='single_choice', comment='题型')
    difficulty = db.Column(db.String(20), default='medium', comment='难度')

    # 关联维度 (多选，所以可能需要JSON或者中间表，这里简化用Category关联主维度)
    category_id = db.Column(db.Integer, db.ForeignKey('question_categories.id'))

    # 状态管理 [cite: 941]
    is_enabled = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关系
    options = db.relationship('QuestionOption', backref='question', cascade="all, delete-orphan")


class QuestionOption(db.Model):
    """题目选项 [cite: 938]"""
    __tablename__ = 'question_options'

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    label = db.Column(db.String(50), comment='选项名：没有/很轻/中等...')
    score = db.Column(db.Integer, comment='分值：1-5')
    sort_order = db.Column(db.Integer, default=0)


# ==========================================
# 4. 后台页面2：AI Agent配置模块 [cite: 950]
# ==========================================

class AIAgentConfig(db.Model):
    __tablename__ = 'ai_agent_configs'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), comment='配置名称')
    model_name = db.Column(db.String(50), default='gpt-4')
    temperature = db.Column(db.Float, default=0.7)

    system_prompt = db.Column(MEDIUMTEXT, nullable=False)

    # 规则配置
    emotion_recognition_rules = db.Column(JSON, comment='情绪识别规则与干预策略')
    style_config = db.Column(JSON, comment='语言风格与禁词')
    scoring_rules = db.Column(JSON, comment='SCL90评分映射规则')

    is_active = db.Column(db.Boolean, default=False, comment='是否为当前生效版本')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AIAgentQuestion(db.Model):
    """AI专用问题库 """
    __tablename__ = 'ai_agent_questions'

    id = db.Column(db.Integer, primary_key=True)
    config_id = db.Column(db.Integer, db.ForeignKey('ai_agent_configs.id'))

    content = db.Column(db.Text, nullable=False, comment='问题内容')
    dimension = db.Column(db.String(50), comment='关联维度')
    priority = db.Column(db.Integer, default=3, comment='优先级 1-5')

    # 评分匹配规则 (明确该问题不同回答的评分逻辑)
    scoring_match_rule = db.Column(db.Text)
    is_enabled = db.Column(db.Boolean, default=True)


class AIAgentConfigVersion(db.Model):
    """AI配置版本管理 (支持回滚) """
    __tablename__ = 'ai_agent_config_versions'

    id = db.Column(db.Integer, primary_key=True)
    original_config_id = db.Column(db.Integer, db.ForeignKey('ai_agent_configs.id'))
    version_tag = db.Column(db.String(50), comment='版本号如 202512初始版')

    # 存储完整配置的快照 (JSON Dump)
    config_snapshot = db.Column(MEDIUMTEXT)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ==========================================
# 5. 后台页面3 & 辅助：数据管理与日志 [cite: 901, 984]
# ==========================================

class ExportRecord(db.Model):
    """数据导出记录 """
    __tablename__ = 'export_records'

    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    export_range = db.Column(JSON, comment='筛选条件快照')
    file_name = db.Column(db.String(255))
    file_url = db.Column(db.String(512))
    file_size = db.Column(db.String(20))
    status = db.Column(db.String(20), default='processing', comment='processing, success, failed')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class OperationLog(db.Model):
    """操作日志 [cite: 985]"""
    __tablename__ = 'operation_logs'

    id = db.Column(db.Integer, primary_key=True)
    operator_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    module = db.Column(db.String(50), comment='操作模块')
    action = db.Column(db.String(50), comment='具体动作')
    target_id = db.Column(db.Integer, nullable=True, comment='操作对象ID')
    ip_address = db.Column(db.String(50))
    result = db.Column(db.String(20), comment='success/failure')
    details = db.Column(db.Text, comment='备注或失败原因')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class UserFeedback(db.Model):
    """用户反馈处理 [cite: 990]"""
    __tablename__ = 'user_feedbacks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    content = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), comment='功能/体验/结果疑问')
    images = db.Column(JSON, comment='上传的图片URL列表')

    status = db.Column(db.String(20), default='pending', comment='pending, processing, replied, closed')
    admin_reply = db.Column(db.Text, comment='管理员回复内容')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)