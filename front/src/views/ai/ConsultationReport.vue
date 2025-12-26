<template>
  <div class="report-page">
    <div class="report-header">
      <el-button link @click="$router.back()"
        ><el-icon><ArrowLeft /></el-icon> 返回</el-button
      >
      <h2 class="title">深度问诊诊断报告</h2>
      <el-button type="primary" plain @click="handlePrint">导出 PDF</el-button>
    </div>

    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>

    <div v-else class="report-content">
      <el-card class="result-card" shadow="never">
        <div class="risk-banner" :class="reportData.final_risk_level">
          <div class="risk-info">
            <span class="label">深度诊断结果</span>
            <h1 class="level-text">{{ getRiskLabel(reportData.final_risk_level) }}</h1>
            <p class="risk-desc">报告生成时间：{{ new Date().toLocaleString() }}</p>
          </div>
          <div class="risk-icon-wrapper">
            <el-icon class="risk-icon">
              <Checked v-if="reportData.final_risk_level === 'good'" />
              <Warning v-else />
            </el-icon>
          </div>
        </div>
      </el-card>

      <el-card class="section-card" header="维度动态分析" shadow="never">
        <el-table :data="scoreTableData" style="width: 100%" border>
          <el-table-column prop="dimension" label="评估维度" />
          <el-table-column prop="initial" label="初始评分" align="center" />
          <el-table-column prop="final" label="深度评估分" align="center" />
          <el-table-column label="分值变动" align="center">
            <template #default="scope">
              <span :class="scope.row.change >= 0 ? 'trend-up' : 'trend-down'">
                {{ scope.row.change > 0 ? '+' : '' }}{{ scope.row.change }}
              </span>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <el-card class="section-card" header="专家干预建议" shadow="never">
        <div class="markdown-body" v-html="renderedMarkdown"></div>
      </el-card>

      <el-collapse class="chat-history-collapse">
        <el-collapse-item title="查看问诊对话记录回顾" name="1">
          <div class="history-list">
            <div
              v-for="(msg, index) in filteredMessages"
              :key="index"
              :class="['history-item', msg.role]"
            >
              <span class="role-tag">{{ msg.role === 'ai' ? 'AI 医生' : '我' }}：</span>
              <p class="content">{{ msg.content }}</p>
            </div>
          </div>
        </el-collapse-item>
      </el-collapse>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { getConsultationDetail } from '@/api/ai'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { ArrowLeft, Checked, Warning } from '@element-plus/icons-vue'

// 定义对话消息的结构
interface ChatMessage {
  role: 'user' | 'ai'
  content: string
}

// 定义报告数据的完整结构
interface ConsultationReportData {
  final_risk_level: 'severe' | 'moderate' | 'good'
  diagnosis_summary: string
  initial_scores: Record<string, number>
  final_scores: Record<string, number>
  score_changes: Record<string, number>
  messages: ChatMessage[]
}

const route = useRoute()
const loading = ref(true)
const reportData = ref<Partial<ConsultationReportData>>({})
const consultationId = route.params.id

// 格式化表格数据
const scoreTableData = computed(() => {
  // 1. 获取数据，如果 reportData 还未加载，则默认为空对象
  const final = reportData.value.final_scores || {}
  const changes = reportData.value.score_changes || {}

  // 2. 遍历维度
  return Object.keys(final).map((dim) => {
    // 3. 关键修复：显式获取数值，并提供默认值 0
    // 这样 TypeScript 就能确定它们是 number 类型，不再报错
    const currentFinal = final[dim] ?? 0
    const currentChange = changes[dim] ?? 0

    return {
      dimension: dim,
      final: currentFinal,
      initial: currentFinal - currentChange, // 现在这里是 number - number，不会报错
      change: currentChange,
    }
  })
})

// 过滤对话记录：跳过索引 0, 1, 2, 3 (前两轮对话，每轮一问一答)
const filteredMessages = computed(() => {
  if (!reportData.value.messages) return []
  return reportData.value.messages.slice(4)
})

// Markdown 渲染
const renderedMarkdown = computed(() => {
  const content = reportData.value.diagnosis_summary || ''
  return DOMPurify.sanitize(marked.parse(content) as string)
})

// 修改函数定义，允许参数 level 为 string 或 undefined
const getRiskLabel = (level?: string): string => {
  if (!level) return '评估中' // 处理 undefined 或空字符串的情况

  const map: Record<string, string> = {
    severe: '风险严重',
    moderate: '中度风险',
    good: '风险受控',
  }

  return map[level] || '评估中'
}

onMounted(async () => {
  try {
    const res = await getConsultationDetail(Number(consultationId))
    reportData.value = res.data
  } finally {
    loading.value = false
  }
})

const handlePrint = () => window.print()
</script>

<style lang="scss" scoped>
.report-page {
  max-width: 900px;
  margin: 0 auto;
  padding: 30px 20px;
  background-color: #f8fafc;
  min-height: 100vh;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;

  .report-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;

    .title {
      font-size: 20px;
      font-weight: 600;
      color: #1e293b;
      margin: 0;
    }
  }

  .section-card {
    margin-bottom: 24px;
    border-radius: 16px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);

    :deep(.el-card__header) {
      border-bottom: 1px solid #f1f5f9;
      font-weight: 600;
      color: #334155;
    }
  }

  // 结果Banner美化
  .result-card {
    border: none;
    background: transparent;
    margin-bottom: 24px;
    :deep(.el-card__body) {
      padding: 0;
    }
  }

  .risk-banner {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 32px;
    border-radius: 16px;
    color: white;
    position: relative;
    overflow: hidden;

    &::after {
      content: '';
      position: absolute;
      right: -20px;
      top: -20px;
      width: 150px;
      height: 150px;
      background: rgba(255, 255, 255, 0.1);
      border-radius: 50%;
    }

    &.severe {
      background: linear-gradient(135deg, #ef4444, #f87171);
    }
    &.moderate {
      background: linear-gradient(135deg, #f59e0b, #fbbf24);
    }
    &.good {
      background: linear-gradient(135deg, #10b981, #34d399);
    }

    .risk-info {
      .label {
        font-size: 14px;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 1px;
      }
      .level-text {
        margin: 8px 0;
        font-size: 32px;
        font-weight: 800;
      }
      .risk-desc {
        margin: 0;
        font-size: 13px;
        opacity: 0.8;
      }
    }

    .risk-icon {
      font-size: 64px;
    }
  }

  // 表格样式调整
  :deep(.el-table) {
    border-radius: 8px;
    overflow: hidden;
    --el-table-header-bg-color: #f8fafc;

    .trend-up {
      color: #ef4444;
      font-weight: 600;
      font-family: monospace;
    }
    .trend-down {
      color: #10b981;
      font-weight: 600;
      font-family: monospace;
    }
  }

  // Markdown内容美化
  .markdown-body {
    line-height: 1.8;
    color: #334155;

    :deep(h3) {
      color: #0f172a;
      border-left: 4px solid #3b82f6;
      padding-left: 12px;
      margin: 24px 0 16px;
    }

    :deep(p) {
      margin-bottom: 12px;
    }

    :deep(ul) {
      background: #f1f5f9;
      padding: 16px 16px 16px 40px;
      border-radius: 8px;
      list-style-type: circle;
    }
  }

  // 对话记录气泡化
  .history-list {
    display: flex;
    flex-direction: column;
    gap: 16px;
    padding: 10px;

    .history-item {
      display: flex;
      flex-direction: column;
      max-width: 85%;
      padding: 12px 16px;
      border-radius: 12px;
      position: relative;

      .role-tag {
        font-size: 12px;
        margin-bottom: 4px;
        font-weight: 600;
        text-transform: uppercase;
      }

      .content {
        margin: 0;
        line-height: 1.5;
        font-size: 14px;
      }

      &.ai {
        align-self: flex-start;
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        color: #1e293b;
        border-bottom-left-radius: 2px;
        .role-tag {
          color: #3b82f6;
        }
      }

      &.user {
        align-self: flex-end;
        background-color: #3b82f6;
        color: #ffffff;
        border-bottom-right-radius: 2px;
        .role-tag {
          color: rgba(255, 255, 255, 0.8);
        }
      }
    }
  }

  // 打印优化
  @media print {
    .report-header,
    .el-collapse {
      display: none;
    }
    .report-page {
      background: white;
      padding: 0;
    }
    .section-card {
      box-shadow: none;
      border: 1px solid #eee;
    }
  }
}
</style>
