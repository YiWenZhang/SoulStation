from .extensions import db
from datetime import datetime
from sqlalchemy.dialects.mysql import JSON, MEDIUMTEXT


# 1. 用户表
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    # 登录凭证
    phone = db.Column(db.String(20), unique=True, index=True)
    password_hash = db.Column(db.String(128))

    # 用户画像
    nickname = db.Column(db.String(50))
    avatar_url = db.Column(db.String(255))

    # 状态
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login_at = db.Column(db.DateTime)

    # 关系：用户的测评记录
    sessions = db.relationship('AssessmentSession', backref='user', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.nickname or self.phone}>'
    def __repr__(self):
        return f'<User {self.username}>'

# 2. AI 配置表 (存储人设)
class AIAgentConfig(db.Model):
    __tablename__ = 'ai_agent_configs'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), comment='配置名称')
    model_name = db.Column(db.String(50), default='gpt-4')
    temperature = db.Column(db.Float, default=0.7)
    system_prompt = db.Column(MEDIUMTEXT, nullable=False, comment='系统提示词')
    variables = db.Column(JSON, comment='预设变量')


# 3. 测评项目表 (首页卡片)
class Assessment(db.Model):
    __tablename__ = 'assessments'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    cover_image = db.Column(db.String(255))

    # JSON 标签
    tags = db.Column(JSON, comment='["心理", "职业"]')
    estimated_time = db.Column(db.String(20))
    is_published = db.Column(db.Boolean, default=True)

    # 关联 AI 配置
    agent_config_id = db.Column(db.Integer, db.ForeignKey('ai_agent_configs.id'))
    agent_config = db.relationship('AIAgentConfig')


# 4. 测评会话表 (核心业务 - 记录做题过程)
class AssessmentSession(db.Model):
    __tablename__ = 'assessment_sessions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=False)

    status = db.Column(db.String(20), default='ongoing', comment='ongoing, completed')
    current_step = db.Column(db.Integer, default=0)
    total_steps = db.Column(db.Integer, default=10)

    # 核心：存储对话历史 (JSON)
    chat_history = db.Column(JSON, default=list)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系：对应的报告
    report = db.relationship('AssessmentReport', backref='session', uselist=False)


# 5. 测评报告表 (结果)
class AssessmentReport(db.Model):
    __tablename__ = 'assessment_reports'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('assessment_sessions.id'), unique=True, nullable=False)

    summary_short = db.Column(db.String(255))
    # 报告内容可能很长，用 MEDIUMTEXT
    detail_content_md = db.Column(MEDIUMTEXT)

    # 雷达图数据
    radar_data = db.Column(JSON)

    generated_at = db.Column(db.DateTime, default=datetime.utcnow)