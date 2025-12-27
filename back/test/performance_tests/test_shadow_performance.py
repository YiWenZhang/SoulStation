import unittest
import sys
import os
import time
import json
import logging

# === 1. 环境配置 ===
# 将项目根目录加入路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src import create_app, db
from src.models import User, AssessmentReport, AIConsultation, AssessmentSession
from src.utils.draft_manager import DraftManager
from src.services.consultation_service import ConsultationService

# 配置日志以便观察实时输出
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)


class TestShadowPerformance(unittest.TestCase):
    def setUp(self):
        # 使用 testing 配置，但我们需要真实的 AI 调用
        # 请确保你的 .env 或环境变量里配置了 AI_API_KEY
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        # === 准备基础数据 ===
        self.user = User(phone='13900000000', nickname='PerfTester')
        db.session.add(self.user)
        db.session.commit()  # Commit to get ID

        self.session = AssessmentSession(user_id=self.user.id, status='completed')
        db.session.add(self.session)
        db.session.commit()

        self.report = AssessmentReport(session_id=self.session.id, risk_level='moderate',
                                       radar_data={"焦虑": 3.0, "抑郁": 2.5})
        db.session.add(self.report)
        db.session.commit()

        # 创建问诊记录
        self.consultation = AIConsultation(
            report_id=self.report.id,
            user_id=self.user.id,
            chat_history=[{"role": "system", "content": "System Init"}],
            sequence_number=1
        )
        db.session.add(self.consultation)
        db.session.commit()

        self.cons_id = self.consultation.id
        # 清理旧草稿
        DraftManager.delete_draft(self.cons_id)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()
        # 测试结束后清理文件
        # DraftManager.delete_draft(self.cons_id) # 注释掉这行，方便你跑完去文件夹里看一眼

    def test_full_shadow_lifecycle(self):
        print("\n" + "=" * 60)
        print("🚀 开始全流程影子分析性能测试")
        print("=" * 60)

        # =========================================================
        # 阶段 1: 正常对话 -> 触发影子分析 (Shadow Trigger)
        # =========================================================
        print("\n[Step 1] 发送第一条消息: '我最近总是失眠，感觉压力好大'...")

        start_time = time.time()
        response = self.client.post('/api/consultation/chat/stream', json={
            'consultation_id': self.cons_id,
            'content': '我最近总是失眠，感觉压力好大，而且有点不想吃饭。'
        })

        # 消费流式响应，确保请求完成
        ai_reply = ""
        for line in response.data.decode('utf-8').split('\n\n'):
            if 'message' in line:
                try:
                    data = json.loads(line.replace('data: ', ''))
                    if data['type'] == 'message': ai_reply += data['content']
                except:
                    pass

        print(f"🤖 AI 回复 (耗时 {time.time() - start_time:.2f}s): {ai_reply[:50]}...")

        # === 关键验证：影子分析是否在后台启动 ===
        print("\n[Step 2] 等待后台影子分析师工作 (Sleep 3s)...")
        time.sleep(3)  # 给后台线程一点时间写文件

        draft = DraftManager.load_draft(self.cons_id)
        if draft:
            print(f"✅ [成功] 检测到实时草稿文件: instance/drafts/draft_{self.cons_id}.json")
            print(f"📄 草稿内容快照: {json.dumps(draft, ensure_ascii=False)[:200]}...")
        else:
            print("❌ [失败] 未检测到草稿文件，影子服务未触发！")
            return

        # =========================================================
        # 阶段 2: AI 主动结束 -> 极速生成报告 (AI Finish)
        # =========================================================
        print("\n[Step 3] 发送结束指令: '我没有问题了，请生成报告'...")
        print("⚡️ 计时开始：测试报告生成速度")

        gen_start_time = time.time()

        # 发送诱导 AI 结束的话术
        response = self.client.post('/api/consultation/chat/stream', json={
            'consultation_id': self.cons_id,
            'content': '好的，我没有其他问题了，请根据刚才的分析给我生成最终诊断报告吧，谢谢医生。'
        })

        # 实时解析流，捕捉 finish 信号
        report_generated = False
        final_summary = ""

        for line in response.data.decode('utf-8').split('\n\n'):
            if not line.strip(): continue
            try:
                # 处理 SSE 格式
                json_str = line.replace('data: ', '')
                packet = json.loads(json_str)

                if packet['type'] == 'finished':
                    report_generated = True
                    # 记录此时的时间
                    gen_end_time = time.time()
                    print(f"✅ 收到 Finished 信号！")
            except:
                pass

        total_time = gen_end_time - gen_start_time if report_generated else 0

        if report_generated:
            print(f"\n⏱️  [性能报告] 报告生成总耗时: {total_time:.4f} 秒")
            if total_time < 5.0:
                print("🏆 结果：极速！影子模式生效中 (通常全量分析需要 10s+)")
            else:
                print("⚠️ 结果：较慢，可能是在进行全量分析")

            # 验证数据库
            updated_cons = AIConsultation.query.get(self.cons_id)
            print(f"\n📝 [数据库验证]")
            print(f"   - 诊断总结长度: {len(updated_cons.diagnosis_summary or '')} 字符")
            print(f"   - 量化分数: {updated_cons.final_scores}")
            print(f"   - 状态: {updated_cons.report.consultation_status}")

            # 验证文件清理
            if not os.path.exists(DraftManager._get_file_path(self.cons_id)):
                print("🧹 [清理验证] 临时草稿文件已自动删除")
            else:
                print("⚠️ [清理验证] 临时文件未删除")
        else:
            print("❌ 测试失败：未收到 finished 信号 (AI 可能没觉得自己该结束)")

    def test_user_manual_finish(self):
        """
        测试 3: 用户主动点击结束按钮 (Manual Finish)
        模拟直接调用生成逻辑，验证是否也能利用草稿加速
        """
        print("\n" + "=" * 60)
        print("🚀 测试用户主动结束 (Manual Finish)")
        print("=" * 60)

        # 1. 先造一个草稿
        fake_draft = {"symptoms": ["人工植入的草稿症状"], "temp_scores": {"焦虑": 4.0}}
        DraftManager.save_draft(self.cons_id, fake_draft)
        print("📝 已植入测试草稿...")

        # 2. 手动调用生成逻辑 (模拟 API /finish 的行为)
        # 这里我们直接调用 Service 里的生成方法，因为那是核心逻辑
        print("⚡️ 触发手动结束逻辑...")
        start = time.time()

        # 模拟：调用 ConsultationService 内部的生成逻辑
        # 注意：实际项目中可能是通过 API 路由调用的
        ai_client = ConsultationService.ai_client if hasattr(ConsultationService, 'ai_client') else None  # Mock or Init
        # 这里我们直接实例化工具来跑
        from src.utils.ai_client import AIClient
        from src.utils.prompt_builder import PromptBuilder

        # 复用 Service 里的逻辑
        data = ConsultationService._generate_report_with_agent_b(
            self.cons_id, AIClient(), PromptBuilder(), self.consultation
        )

        duration = time.time() - start
        print(f"⏱️  手动结束耗时: {duration:.4f} 秒")

        # 验证结果是否包含草稿里的信息 (证明利用了草稿)
        # 这里的 AI 是真实的，它会读草稿。如果它够聪明，它会在报告里提到“人工植入的草稿症状”
        # 但由于 AI 输出不可控，我们主要看是否报错和时间
        self.assertIsNotNone(data.get('diagnosis_summary'))
        print("✅ 手动结束成功生成报告")


if __name__ == '__main__':
    unittest.main()