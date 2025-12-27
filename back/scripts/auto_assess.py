import sys
import os
import random
import json

# 环境配置
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src import create_app, db
from src.models import User, AssessmentSession, Question
from src.utils.common import calculate_scl90_report_logic


def run_auto_assessment(user_id, count=10):
    app = create_app('default')
    with app.app_context():
        user = db.session.get(User, user_id)
        if not user:
            print(f"❌ 找不到 ID 为 {user_id} 的用户")
            return

        # 获取题目与维度的对应关系
        questions = Question.query.all()
        dim_map = {}
        for q in questions:
            if q.category_id not in dim_map: dim_map[q.category_id] = []
            dim_map[q.category_id].append(str(q.id))
        cat_ids = list(dim_map.keys())

        # --- 核心改进：固定配额分配，确保三种结果都有 ---
        # 5个Good, 3个Moderate, 2个Severe
        targets = ["good"] * 5 + ["moderate"] * 3 + ["severe"] * 2
        random.shuffle(targets)  # 打乱顺序让历史记录看起来更随机

        for i in range(len(targets)):
            target = targets[i]

            if target == "good":
                limit = 1.9
                high_risk_count = 0
            elif target == "moderate":
                limit = 2.9
                # 仅随机 1-2 个维度偏高，防止“满堂红”
                high_risk_count = random.randint(1, 2)
            else:  # severe
                limit = 5.0
                # 随机 3-5 个维度偏高
                high_risk_count = random.randint(3, 5)

            print(f"正在模拟第 {i + 1}/{len(targets)} 次测评 [目标: {target.upper()}]...")

            high_risk_cats = random.sample(cat_ids, high_risk_count) if high_risk_count > 0 else []

            chat_history = {}
            for cat_id, q_ids in dim_map.items():
                is_high = cat_id in high_risk_cats

                for q_id in q_ids:
                    if target == "good":
                        # 全员健康：1分(90%)，偶尔2分
                        val = random.choices([1, 2], weights=[90, 10])[0]
                    elif target == "moderate":
                        if is_high:
                            # 目标是中度：高风险维度控制在 2-3 分
                            val = random.choices([2, 3], weights=[40, 60])[0]
                        else:
                            val = random.choices([1, 2], weights=[85, 15])[0]
                    else:  # severe
                        if is_high:
                            # 目标是严重：高风险维度给 3-5 分
                            val = random.choices([3, 4, 5], weights=[20, 50, 30])[0]
                        else:
                            val = random.choices([1, 2, 3], weights=[70, 20, 10])[0]

                    chat_history[q_id] = val

                # --- 维度分数硬拦截：确保不越级 ---
                current_dim_scores = [chat_history[qid] for qid in q_ids]
                current_avg = sum(current_dim_scores) / len(q_ids)

                if current_avg > limit:
                    # 强行拉低分数以符合目标等级
                    for qid in q_ids:
                        chat_history[qid] = int(limit)

            # 1. 保存会话
            session = AssessmentSession(
                user_id=user.id, mode='questionnaire', status='ongoing',
                current_step=90, total_steps=90, chat_history=chat_history
            )
            db.session.add(session)
            db.session.flush()

            # 2. 调用逻辑
            try:
                # 使用封装在 utils 中的计算逻辑
                report = calculate_scl90_report_logic(session)
                session.status = 'completed'
                db.session.add(report)
                db.session.commit()
                print(f"   ✅ 完成！等级: {report.risk_level.upper()} | 摘要: {report.summary_short}")
            except Exception as e:
                db.session.rollback()
                print(f"   ❌ 出错: {str(e)}")


if __name__ == "__main__":
    run_auto_assessment(user_id=1, count=10)