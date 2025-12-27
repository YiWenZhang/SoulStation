from src import create_app, db
from src.models import AssessmentSession, AssessmentReport
import json
from datetime import datetime

app = create_app('default')  # 或者你的配置名
with app.app_context():
    # 模拟数据生成逻辑
    for i in range(10):
        session = AssessmentSession(
            user_id=1,  # 替换为你的真实用户ID
            mode='questionnaire',
            status='completed'
        )
        db.session.add(session)
        db.session.flush()  # 获取 session.id

        report = AssessmentReport(
            session_id=session.id,
            summary_short=f"测试自动生成报告 {i + 1}",
            radar_data={"焦虑": 2.0 + (i * 0.1), "抑郁": 1.5 + (i * 0.2)},  # 模拟分数变化
            risk_level='moderate' if i > 5 else 'mild',
            total_score=150.0 + i,
            total_avg=1.6 + (i * 0.1)
        )
        db.session.add(report)

    db.session.commit()
    print("成功插入10条模拟测评数据")