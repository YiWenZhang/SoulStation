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
    last_assessment_at = db.Column(db.DateTime, comment='最近一次完成测评的时间')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login_at = db.Column(db.DateTime)

    # 关系
    sessions = db.relationship('AssessmentSession', backref='user', lazy='dynamic')


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
    # detail_content_md = db.Column(MEDIUMTEXT, comment='Markdown详情')
    radar_data = db.Column(db.JSON)

    # 数据管理页所需的筛选字段
    # risk_level: 'good', 'mild', 'moderate', 'severe'
    risk_level = db.Column(db.String(20), index=True, comment='风险等级')

    # 存储高风险维度列表，如 ["anxiety", "depression"]，用于高级搜索
    high_risk_dimensions = db.Column(JSON, comment='核心高风险维度')

    # === 新增：只存核心数值，不存冗余文案 ===
    total_score = db.Column(db.Float, default=0.0, comment='总分')
    total_avg = db.Column(db.Float, default=0.0, comment='总均分')

    # === 【修改】AI 问诊相关字段 ===

    # 1. 新增：问诊次数计数器
    consultation_count = db.Column(db.Integer, default=0, comment='AI问诊次数')

    # 2. 修改：问诊状态 (建议保留，用于标记当前最新的一次问诊是否正在进行中)
    consultation_status = db.Column(db.String(20), default='none', comment='当前问诊状态: none, ongoing, completed')

    # 3. 修改：关联关系改为一对多 (uselist=True 或默认不写，去掉 uselist=False)
    # 将属性名从 consultation 改为 consultations 更加语义化
    consultations = db.relationship('AIConsultation', backref='report', lazy='dynamic')

    generated_at = db.Column(db.DateTime, default=datetime.utcnow)


# ==========================================
# 3. 后台页面1：题库管理模块 [cite: 925]
# ==========================================

class QuestionCategory(db.Model):
    """题目分类树 (SCL90维度) [cite: 928]"""
    __tablename__ = 'question_categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # 如：躯体化、焦虑



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
# 4. AI Agent配置模块
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







# ==========================================
# 【新增】 维度解释规则表 (专门存文案)
# ==========================================
class AssessmentRule(db.Model):
    __tablename__ = 'assessment_rules'

    id = db.Column(db.Integer, primary_key=True)
    dimension_name = db.Column(db.String(50), index=True, comment='维度: 焦虑/抑郁...')
    level = db.Column(db.Integer, comment='等级: 1-5')
    level_label = db.Column(db.String(20), comment='标签: 无/轻微/严重')
    description = db.Column(db.Text, comment='解释文案')

    # 联合唯一索引，确保 (维度+等级) 只有一条记录
    __table_args__ = (
        db.UniqueConstraint('dimension_name', 'level', name='uq_dimension_level'),
    )


# ==========================================
# 【新增】AI 问诊记录表
# 专门存储基于某份报告进行的 AI 心理医生对话及结论
# ==========================================
class AIConsultation(db.Model):
    __tablename__ = 'ai_consultations'

    id = db.Column(db.Integer, primary_key=True)

    # === 1.关联外键 ===
    # 去除 unique=True，允许同一 report_id 对应多条记录
    report_id = db.Column(db.Integer, db.ForeignKey('assessment_reports.id'), nullable=False, index=True)

    # === 2.复诊次序 ===
    # 记录这是第几次问诊 (如：1 代表初诊，2 代表第一次复诊...)
    sequence_number = db.Column(db.Integer, default=1, comment='问诊次序')

    # === 3.问诊数据 ===
    chat_history = db.Column(JSON, default=list, comment='本次问诊的对话记录')
    diagnosis_summary = db.Column(MEDIUMTEXT, comment='本次AI生成的诊断总结与建议')

    # --- 【新增字段】用于存储量化数据 ---
    # 存储 AI 修正后的维度分数，例如：{"抑郁": 3.25, "焦虑": 2.10, ...}
    final_scores = db.Column(db.JSON, nullable=True)
    # 存储对比初始问卷的分数变化，例如：{"抑郁": 0.5, "焦虑": -0.2, ...}
    score_changes = db.Column(db.JSON, nullable=True)
    # 存储 AI 问诊后最终判定的风险等级：'good', 'moderate', 'severe'
    final_risk_level = db.Column(db.String(20), nullable=True)
    # 存储 AI 评估的百分比/好转率等描述性统计
    improvement_rate = db.Column(db.Float, nullable=True)

    current_step = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)