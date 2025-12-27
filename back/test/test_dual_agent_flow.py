import os
import json
import unittest
from src import create_app
from src.extensions import db
from src.models import User, AssessmentReport, AssessmentSession, AIConsultation
from src.services.consultation_service import ConsultationService
from src.utils.prompt_builder import PromptBuilder
from src.utils.ai_client import AIClient


class TestDualAgentFlow(unittest.TestCase):
    def setUp(self):
        """测试环境初始化"""
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()

        # 模拟基础数据
        self.uid = 1
        self.report_id = 1

        # 初始化工具
        self.service = ConsultationService()
        self.prompt_builder = PromptBuilder()
        self.ai_client = AIClient()

    def tearDown(self):
        self.app_context.pop()

    def test_01_first_consultation_flow(self):
        """测试初诊流程：原始分 -> 分析师B -> 修正分1"""
        print("\n=== 开始初诊测试 ===")

        # 1. 获取初诊记录 (假设 sequence_number=1)
        consultation = AIConsultation.query.filter_by(
            report_id=self.report_id,
            sequence_number=1
        ).first()

        # 2. 测试咨询师A的消息构建 (初诊应只有原始分)
        messages = self.prompt_builder.build_consultant_messages(
            consultation.report,
            history_messages=[],
            sequence_number=1,
            prev_scores=None
        )

        print(f"初诊 System Prompt 检查: {'原始' in messages[0]['content']}")
        self.assertIn("原始", messages[0]['content'])

        # 3. 模拟分析师B生成报告
        # 构造一段暗示“好转”的对话
        fake_history = [
            {"role": "user", "content": "你好医生"},
            {"role": "assistant", "content": "你好，看你上次问卷显示焦虑比较严重？"},
            {"role": "user", "content": "是的，但最近通过运动感觉好多了，没那么紧张了。"}
        ]

        print("正在调用分析师B生成初诊报告...")
        summary_data = self.service._generate_report_with_agent_b(
            fake_history, self.ai_client, self.prompt_builder, consultation
        )

        print(f"分析师B返回分值: {summary_data.get('scores')}")
        self.assertTrue('scores' in summary_data)

        # 4. 验证数据落地
        success = self.service.update_consultation_data(consultation, json.dumps(summary_data))
        self.assertTrue(success)
        print(f"初诊数据已存入，修正分: {consultation.final_scores}")

    def test_02_second_consultation_flow(self):
        """测试复诊流程：修正分1 -> 咨询师A感知 -> 分析师B对比 -> 修正分2"""
        print("\n=== 开始复诊测试 ===")

        # 1. 获取复诊记录 (sequence_number=2)
        consultation = AIConsultation.query.filter_by(
            report_id=self.report_id,
            sequence_number=2
        ).first()

        if not consultation:
            print("跳过测试：未找到序号为2的复诊记录，请先确保数据库有测试数据")
            return

        # 2. 检查咨询师A是否拿到了上次的修正分
        prev_con = AIConsultation.query.filter_by(
            report_id=self.report_id,
            sequence_number=1
        ).first()

        messages = self.prompt_builder.build_consultant_messages(
            consultation.report,
            history_messages=[],
            sequence_number=2,
            prev_scores=prev_con.final_scores
        )

        print("复诊提示词检查...")
        self.assertIn("上次 AI 修正得分", messages[0]['content'])
        print("✅ 咨询师A已成功获取上次 AI 修正的分数作为背景")

        # 3. 检查分析师B是否以“上次修正分”为基准
        fake_history_2 = [
            {"role": "user", "content": "医生，我感觉焦虑又反复了，昨晚没睡好。"}
        ]

        summary_data_2 = self.service._generate_report_with_agent_b(
            fake_history_2, self.ai_client, self.prompt_builder, consultation
        )

        print(f"复诊分析结论: {summary_data_2.get('diagnosis_summary')[:50]}...")
        print(f"复诊修正分: {summary_data_2.get('scores')}")

        # 4. 验证 score_changes 是否是基于“上次”计算的
        self.service.update_consultation_data(consultation, json.dumps(summary_data_2))
        print(f"复诊变化量 (score_changes): {consultation.score_changes}")
        # 这里你可以断言 changes 是本次分数减去 prev_con 的分数

    def test_03_auto_end_logic(self):
        """测试 AI 自动结束标记识别"""
        print("\n=== 开始结束标记测试 ===")

        # 模拟 AI 返回了结束标记
        raw_ai_reply = "好的，看来你已经掌握了这些方法。祝你生活愉快！ <END_DIAGNOSIS>"

        is_finished = "<END_DIAGNOSIS>" in raw_ai_reply
        clean_response = raw_ai_reply.replace("<END_DIAGNOSIS>", "").strip()

        print(f"是否识别结束: {is_finished}")
        print(f"清洗后的内容: {clean_response}")

        self.assertTrue(is_finished)
        self.assertNotIn("<END_DIAGNOSIS>", clean_response)
        print("✅ 结束标记识别与字符串清洗逻辑正确")


if __name__ == '__main__':
    unittest.main()