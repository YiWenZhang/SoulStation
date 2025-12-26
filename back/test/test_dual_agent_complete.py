import unittest
from unittest.mock import patch, MagicMock, ANY
import sys
import os
import json

# 路径配置
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src import create_app, db
from src.models import User, AssessmentReport, AIConsultation, AssessmentSession, AIAgentConfig
from src.services.consultation_service import ConsultationService


class TestDualAgentSystem(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # 1. 准备基础数据
        user = User(phone='10086', nickname='DualAgentUser')
        db.session.add(user)
        db.session.commit()

        session = AssessmentSession(user_id=user.id, status='completed')
        db.session.add(session)
        db.session.commit()

        self.report = AssessmentReport(
            session_id=session.id,
            risk_level='moderate',
            radar_data={"焦虑": 2.5, "抑郁": 1.5}
        )
        db.session.add(self.report)
        db.session.commit()

        # 2. 【关键】在数据库中写入知识配置
        # 我们要验证 PromptBuilder 是否真的读了这个配置
        self.db_prompt_content = "【这是来自数据库的SCL-90核心规则KnowledgeBase】"
        config = AIAgentConfig(
            name="Default Config",
            system_prompt=self.db_prompt_content,
            is_active=True
        )
        db.session.add(config)

        # 3. 创建初始问诊记录
        self.consultation = AIConsultation(
            report_id=self.report.id,
            user_id=user.id,
            chat_history=[],
            sequence_number=1
        )
        db.session.add(self.consultation)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    @patch('src.services.consultation_service.AIClient')
    def test_dual_agent_workflow(self, MockAIClient):
        """
        完整测试：数据库配置读取 -> 咨询师对话 -> 结束触发 -> 分析师总结 -> 结果入库
        """
        print("\n=== 开始双智能体全流程测试 ===")
        mock_ai_instance = MockAIClient.return_value

        # --- 场景模拟 ---

        # 1. 设置模拟返回
        # 第一次调用 (咨询师流式): 返回 "好的<END_DIAGNOSIS>" 触发结束
        # 注意：get_stream_response 是生成器
        def stream_side_effect(messages, **kwargs):
            # 【验证点1】检查咨询师是否继承了数据库配置
            system_msg = next((m['content'] for m in messages if m['role'] == 'system'), "")
            if "【这是来自数据库的SCL-90核心规则KnowledgeBase】" in system_msg:
                print("✅ [Pass] 智能体A(咨询师) 成功读取数据库配置")
            else:
                print("❌ [Fail] 智能体A 未读取数据库配置！")

            yield "好的，请注意休息。"
            yield "<END_DIAGNOSIS>"

        mock_ai_instance.get_stream_response.side_effect = stream_side_effect

        # 第二次调用 (分析师非流式): 返回 JSON
        mock_ai_instance.get_response.return_value = json.dumps({
            "diagnosis_summary": "### 最终诊断\n用户有中度焦虑。",
            "scores": {"焦虑": 2.8, "抑郁": 1.6}
        })

        # --- 执行业务逻辑 ---
        # 模拟用户发送 "我没问题了"
        generator = ConsultationService.process_chat_stream(self.consultation.id, "我没问题了")

        # 消费生成器，驱动代码运行
        results = list(generator)

        # --- 验证环节 ---

        # 2. 【验证点2】参数隔离 (Temperature)
        # 获取所有调用记录
        # get_stream_response 被调用了一次 (咨询师)
        # get_response 被调用了一次 (分析师)

        # 检查咨询师参数
        args_consultant, kwargs_consultant = mock_ai_instance.get_stream_response.call_args
        if kwargs_consultant.get('temperature') == 0.7:
            print("✅ [Pass] 智能体A(咨询师) 参数正确: temperature=0.7")
        else:
            print(f"❌ [Fail] 智能体A 参数错误: {kwargs_consultant}")

        # 检查分析师参数
        args_analyst, kwargs_analyst = mock_ai_instance.get_response.call_args
        if kwargs_analyst.get('temperature') == 0.2 and \
                kwargs_analyst.get('response_format') == {"type": "json_object"}:
            print("✅ [Pass] 智能体B(分析师) 参数正确: temperature=0.2, JSON Mode开启")
        else:
            print(f"❌ [Fail] 智能体B 参数错误: {kwargs_analyst}")

        # 3. 【验证点3】分析师是否也读取了数据库配置
        analyst_messages = args_analyst[0]
        analyst_system = next((m['content'] for m in analyst_messages if m['role'] == 'system'), "")
        if self.db_prompt_content in analyst_system:
            print("✅ [Pass] 智能体B(分析师) 成功读取数据库配置")
        else:
            print("❌ [Fail] 智能体B 未读取数据库配置！")

        # 4. 【验证点4】数据库最终状态
        # 重新从数据库读取记录
        updated_cons = AIConsultation.query.get(self.consultation.id)

        # 检查总结是否写入
        if "### 最终诊断" in updated_cons.diagnosis_summary:
            print("✅ [Pass] 诊断总结已存入数据库")
        else:
            print("❌ [Fail] 诊断总结未存入！")

        # 检查分数是否解析并写入
        # 注意：SQLAlchemy JSON字段读取回来通常是 dict
        final_scores = updated_cons.final_scores
        if final_scores and final_scores.get('焦虑') == 2.8:
            print("✅ [Pass] 量化分数已解析并存入 JSON 字段")
        else:
            print(f"❌ [Fail] 分数存入失败: {final_scores}")

        # 检查状态
        if updated_cons.report.consultation_status == 'completed':
            print("✅ [Pass] 问诊状态已更新为 completed")
        else:
            print("❌ [Fail] 问诊状态未更新")


if __name__ == '__main__':
    unittest.main()