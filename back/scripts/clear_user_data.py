import sys
import os

# 将项目根目录加入路径，确保能导入 src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src import create_app, db
from src.models import User, AssessmentSession, AssessmentReport, AIConsultation


def clear_user_history(user_id):
    app = create_app('default')
    with app.app_context():
        # 1. 检查用户是否存在
        user = User.query.get(user_id)
        if not user:
            print(f"❌ 错误：找不到 ID 为 {user_id} 的用户。")
            return

        print(f"⚠️ 正在清空用户 [{user.nickname}] (ID: {user_id}) 的所有测评与问诊历史...")

        try:
            # 2. 删除 AI 问诊记录 (AIConsultation)
            # 这些记录关联了 user_id
            consultations_deleted = AIConsultation.query.filter_by(user_id=user_id).delete()
            print(f"   - 已删除 {consultations_deleted} 条 AI 问诊记录")

            # 3. 删除 测评报告 (AssessmentReport)
            # 报告通过 session_id 间接关联用户，我们需要先找到该用户的所有 session_ids
            session_ids = [s.id for s in AssessmentSession.query.filter_by(user_id=user_id).all()]

            if session_ids:
                reports_deleted = AssessmentReport.query.filter(AssessmentReport.session_id.in_(session_ids)).delete(
                    synchronize_session=False)
                print(f"   - 已删除 {reports_deleted} 条问卷测评报告")

                # 4. 删除 测评会话 (AssessmentSession)
                sessions_deleted = AssessmentSession.query.filter(AssessmentSession.id.in_(session_ids)).delete(
                    synchronize_session=False)
                print(f"   - 已删除 {sessions_deleted} 条问卷测评会话")
            else:
                print("   - 该用户暂无测评记录")

            # 5. 提交变更
            db.session.commit()
            print(f"✅ 成功！用户 {user_id} 的历史数据已完全清空，用户信息保留。")

        except Exception as e:
            db.session.rollback()
            print(f"❌ 清空失败：{str(e)}")


if __name__ == "__main__":
    # 在这里输入你想清空的用户 ID
    # 建议先在数据库查一下，通常第一个注册的是 1
    TARGET_USER_ID = 1

    # 增加一个简单的二次确认
    confirm = input(f"确认要清空用户 {TARGET_USER_ID} 的所有历史数据吗？(y/n): ")
    if confirm.lower() == 'y':
        clear_user_history(TARGET_USER_ID)
    else:
        print("操作已取消。")