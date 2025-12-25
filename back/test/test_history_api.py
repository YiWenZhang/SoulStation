import pytest
import json
from datetime import datetime, timedelta
# 👇 关键修改 1：引入哈希生成函数
from werkzeug.security import generate_password_hash
from src import create_app
from src.extensions import db
# 👇 关键修改 2：必须引入 AIConsultation 模型，否则查询时会报错
from src.models import User, AssessmentSession, AssessmentReport, AIConsultation


# ==========================================
# 1. 测试环境配置 (Fixture)
# ==========================================
@pytest.fixture
def app():
    """创建一个独立的测试用 Flask 应用"""
    app = create_app('testing')

    # 使用内存数据库，确保测试互不干扰
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False
    })

    with app.app_context():
        db.create_all()  # 创建表结构
        yield app
        db.session.remove()
        db.drop_all()  # 清空数据


@pytest.fixture
def client(app):
    return app.test_client()


# ==========================================
# 2. 核心测试逻辑
# ==========================================
def test_get_history_list(client, app):
    """测试：获取历史问卷列表及其关联的 AI 问诊状态"""

    with app.app_context():
        # --- 步骤 1: 准备数据 ---

        # A. 创建用户
        user = User(nickname='测试者', phone='13800000000')
        # 👇 关键修改 3：直接赋值 password_hash
        user.password_hash = generate_password_hash('123456')
        db.session.add(user)
        db.session.commit()
        uid = user.id

        # B. 场景一：用户做了一次问卷(scale)，但还没有进行问诊
        # 模拟 2 天前做的
        session1 = AssessmentSession(
            user_id=uid,
            mode='scale',
            status='completed',
            updated_at=datetime.utcnow() - timedelta(days=2)
        )
        db.session.add(session1)
        db.session.commit()

        report1 = AssessmentReport(
            session_id=session1.id,
            summary_short='轻度焦虑',
            risk_level='mild',
            generated_at=datetime.utcnow() - timedelta(days=2),
            consultation_count=0  # 初始为0
        )
        db.session.add(report1)
        db.session.commit()

        # C. 场景二：用户做了第二次问卷(ai_chat)，并且进行过 1 次 AI 问诊
        # 模拟刚刚完成
        session2 = AssessmentSession(
            user_id=uid,
            mode='ai_chat',
            status='completed',
            updated_at=datetime.utcnow()
        )
        db.session.add(session2)
        db.session.commit()

        report2 = AssessmentReport(
            session_id=session2.id,
            summary_short='状态良好',
            risk_level='good',
            generated_at=datetime.utcnow(),
            consultation_count=1  # 记录上写着1次
        )
        db.session.add(report2)
        db.session.commit()

        # 添加具体的问诊记录 (用于验证 summary_snippet 和 consultations 列表)
        consultation = AIConsultation(
            report_id=report2.id,
            user_id=uid,
            sequence_number=1,  # 第1次
            diagnosis_summary='建议保持心情愉快，多运动...',  # 模拟已有诊断结果
            updated_at=datetime.now()
        )
        db.session.add(consultation)
        db.session.commit()

        print(f"\n[测试准备] 用户ID: {uid}")
        print(f"[测试准备] 报告1 (ID: {report1.id}): 无问诊")
        print(f"[测试准备] 报告2 (ID: {report2.id}): 有1条问诊记录")

    # --- 步骤 2: 调用接口 ---
    # 注意：根据你的要求，这个接口应该添加到了 api.py 中
    response = client.get(f'/api/history/list?uid={uid}')

    # --- 步骤 3: 验证结果 ---
    assert response.status_code == 200, f"接口 HTTP 状态码应为 200, 实际为 {response.status_code}"

    res_json = response.get_json()
    # 打印返回结果方便调试
    print(f"\n[接口返回] {json.dumps(res_json, ensure_ascii=False, indent=2)}")

    assert res_json['code'] == 200
    data = res_json['data']

    # 验证 1: 应该返回 2 条历史问卷记录
    assert len(data) == 2, "应该查到 2 份历史问卷"

    # 验证 2: 排序应该是时间倒序（最新的 report2 在前）
    first_item = data[0]
    second_item = data[1]

    assert first_item['report_id'] == report2.id, "最新的问卷应该排在第一位"
    assert second_item['report_id'] == report1.id

    # 验证 3: 检查核心嵌套结构 (Consultations)
    # report2 应该有问诊列表
    assert 'consultations' in first_item, "返回数据应该包含 consultations 字段"
    cons_list = first_item['consultations']
    assert len(cons_list) == 1, "report2 应该有 1 条问诊记录"

    cons_item = cons_list[0]
    assert cons_item['sequence_number'] == 1
    assert '建议保持' in cons_item['summary_snippet']
    assert cons_item['status'] == 'completed'

    # report1 应该为空列表
    assert 'consultations' in second_item
    assert len(second_item['consultations']) == 0

    print("\n✅ 测试通过：接口逻辑正确！")