<!-- views/History/CombinedReportView.vue -->
<template>
  <div class="report-container">
    <!-- 背景装饰 -->
    <div class="background-decoration">
      <div class="bubble bubble-1"></div>
      <div class="bubble bubble-2"></div>
      <div class="bubble bubble-3"></div>
      <div class="floating-icon icon-1">📊</div>
      <div class="floating-icon icon-2">💬</div>
      <div class="floating-icon icon-3">💡</div>
    </div>

    <!-- 顶部导航 -->
    <header class="page-header">
      <div class="header-content">
        <div class="header-left">
          <div class="logo-section" @click="goHome">
            <div class="logo-icon">🌸</div>
            <div class="logo-text">
              <h1 class="site-title">心灵驿站</h1>
              <p class="site-subtitle">Mental Harbor</p>
            </div>
          </div>
        </div>
        <div class="header-center">
          <h1 class="page-title">
            <span class="title-icon">{{ hasConsultation ? '🩺' : '📋' }}</span>
            {{ hasConsultation ? '综合诊断报告' : '心理健康测评报告' }}
            <span class="title-badge" :class="displayRiskClass" v-if="reportData">
              {{ displayRiskLabel }}
            </span>
          </h1>
          <p class="page-subtitle">
            {{
              hasConsultation
                ? '测评分析 + AI问诊建议，全方位守护心灵健康'
                : '专业分析，科学建议，助力心灵成长'
            }}
          </p>
        </div>
        <div class="header-right">
          <div class="action-buttons">
            <button
              class="action-btn chat-btn"
              @click="startChat"
              v-if="reportData && !hasConsultation"
            >
              <span class="btn-icon">💬</span>
              <span class="btn-text">开始AI问诊</span>
            </button>
            <button class="action-btn back-btn" @click="goBack">
              <span class="btn-icon">←</span>
              <span class="btn-text">返回</span>
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="loading-content">
        <div class="loading-animation">
          <div class="loading-circle"></div>
          <div class="loading-circle"></div>
          <div class="loading-circle"></div>
        </div>
        <h3 class="loading-title">正在加载报告</h3>
        <p class="loading-subtitle">数据整理中，请稍候...</p>
      </div>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error-state">
      <div class="error-content">
        <div class="error-icon">❌</div>
        <h3 class="error-title">{{ error.title }}</h3>
        <p class="error-message">{{ error.message }}</p>
        <div class="error-actions">
          <button class="error-btn primary" @click="retry">重新加载</button>
          <button class="error-btn secondary" @click="goHome">返回首页</button>
        </div>
      </div>
    </div>

    <!-- 主内容区域 -->
    <main class="main-content" v-else-if="reportData">
      <!-- 报告导航标签 -->
      <div class="report-tabs" v-if="hasConsultation">
        <button
          class="tab-btn"
          :class="{ active: activeSection === 'consultation' }"
          @click="activeSection = 'consultation'"
        >
          <span class="tab-icon">🤖</span>
          <span class="tab-text">AI问诊报告</span>
        </button>
        <button
          class="tab-btn"
          :class="{ active: activeSection === 'assessment' }"
          @click="activeSection = 'assessment'"
        >
          <span class="tab-icon">📊</span>
          <span class="tab-text">测评报告</span>
        </button>
        <button
          class="tab-btn"
          :class="{ active: activeSection === 'all' }"
          @click="activeSection = 'all'"
        >
          <span class="tab-icon">📑</span>
          <span class="tab-text">完整报告</span>
        </button>
      </div>

      <!-- ==================== AI问诊部分 ==================== -->
      <section
        class="consultation-section"
        v-if="hasConsultation && (activeSection === 'consultation' || activeSection === 'all')"
      >
        <div class="section-header">
          <h2 class="section-title">
            <span class="section-icon">🤖</span>
            AI 问诊分析报告
          </h2>
          <div class="section-meta">
            <!-- 删除了就诊日期，只保留问诊次数和状态 -->
            <span class="meta-tag">
              <span class="tag-icon">🔢</span>
              第 {{ consultationData?.sequence_number }} 次问诊
            </span>
            <span class="meta-tag status-tag" :class="consultationData?.status">
              <span class="tag-icon">{{
                consultationData?.status === 'finished' ? '✅' : '⏳'
              }}</span>
              {{ consultationData?.status === 'finished' ? '已完成' : '进行中' }}
            </span>
          </div>
        </div>

        <div class="consultation-content">
          <!-- 风险等级变化卡片 -->
          <div class="card risk-change-card" v-if="consultationData?.final_risk_level">
            <div class="card-header">
              <h3 class="card-title">
                <span class="title-icon">🎯</span>
                风险等级评估
              </h3>
            </div>
            <div class="risk-change-body">
              <div class="risk-comparison">
                <div class="risk-item initial">
                  <div class="risk-label">初始评估</div>
                  <div
                    class="risk-badge"
                    :class="getRiskClass(consultationData?.initial_risk_level)"
                  >
                    <span class="risk-emoji">{{
                      getRiskEmoji(consultationData?.initial_risk_level)
                    }}</span>
                    <span class="risk-text">{{
                      getRiskLabel(consultationData?.initial_risk_level)
                    }}</span>
                  </div>
                </div>
                <div class="risk-arrow">
                  <span class="arrow-icon">→</span>
                  <span class="arrow-label">AI修正</span>
                </div>
                <div class="risk-item final">
                  <div class="risk-label">修正评估</div>
                  <div class="risk-badge" :class="getRiskClass(consultationData?.final_risk_level)">
                    <span class="risk-emoji">{{
                      getRiskEmoji(consultationData?.final_risk_level)
                    }}</span>
                    <span class="risk-text">{{
                      getRiskLabel(consultationData?.final_risk_level)
                    }}</span>
                  </div>
                </div>
              </div>
              <div class="risk-note" v-if="riskChanged">
                <span class="note-icon">💡</span>
                <span class="note-text">
                  经AI问诊深入了解后，风险等级从「{{
                    getRiskLabel(consultationData?.initial_risk_level)
                  }}」 调整为「{{ getRiskLabel(consultationData?.final_risk_level) }}」
                </span>
              </div>
            </div>
          </div>

          <!-- 分数对比雷达图 -->
          <div class="card comparison-chart-card" v-if="hasScoreComparison">
            <div class="card-header">
              <h3 class="card-title">
                <span class="title-icon">📈</span>
                分数对比雷达图
              </h3>
              <div class="legend-inline">
                <span class="legend-item">
                  <span class="legend-dot initial"></span>
                  上次评估
                </span>
                <span class="legend-item">
                  <span class="legend-dot final"></span>
                  AI修正
                </span>
              </div>
            </div>
            <div class="chart-container">
              <div ref="comparisonChartRef" class="chart"></div>
            </div>
          </div>

          <!-- 分数变化详情 -->
          <div class="card score-changes-card" v-if="hasScoreChanges">
            <div class="card-header">
              <h3 class="card-title">
                <span class="title-icon">📊</span>
                维度分数变化
              </h3>
            </div>
            <div class="score-changes-body">
              <div
                class="change-item"
                v-for="item in scoreChangesList"
                :key="item.dimension"
                :class="getChangeClass(item.change)"
              >
                <div class="change-dimension">{{ item.dimension }}</div>
                <div class="change-scores">
                  <span class="score-initial">{{ item.initial }}</span>
                  <span class="score-arrow">→</span>
                  <span class="score-final">{{ item.final }}</span>
                </div>
                <div class="change-value" :class="getChangeClass(item.change)">
                  <span class="change-icon">{{
                    item.change > 0 ? '↑' : item.change < 0 ? '↓' : '—'
                  }}</span>
                  <span class="change-number"
                    >{{ item.change > 0 ? '+' : '' }}{{ item.change.toFixed(2) }}</span
                  >
                </div>
              </div>
            </div>
          </div>

          <!-- AI诊断总结卡片 (Markdown渲染，已过滤备注和量化评估) -->
          <div class="card diagnosis-card full-width">
            <div class="card-header">
              <h3 class="card-title">
                <span class="title-icon">📝</span>
                AI 诊断总结
              </h3>
              <div class="ai-badge">
                <span class="badge-icon">✨</span>
                <span class="badge-text">AI 智能分析</span>
              </div>
            </div>
            <div class="diagnosis-body">
              <div
                v-if="cleanedDiagnosisSummaryHtml"
                class="markdown-content diagnosis-markdown"
                v-html="cleanedDiagnosisSummaryHtml"
              ></div>
              <div v-else class="no-diagnosis">
                <div class="no-data-icon">💭</div>
                <p>问诊尚未完成，暂无诊断总结</p>
              </div>
            </div>
          </div>

          <!-- 对话回顾卡片 -->
          <div class="card chat-card full-width">
            <div class="card-header">
              <h3 class="card-title">
                <span class="title-icon">💬</span>
                对话回顾
              </h3>
              <div class="chat-meta">
                <span class="chat-count">{{ displayableChatHistory.length }} 轮对话</span>
                <button
                  class="expand-btn"
                  @click="chatExpanded = !chatExpanded"
                  v-if="displayableChatHistory.length > 0"
                >
                  {{ chatExpanded ? '收起' : '展开全部' }}
                  <span class="expand-icon">{{ chatExpanded ? '↑' : '↓' }}</span>
                </button>
              </div>
            </div>
            <div class="chat-body" :class="{ expanded: chatExpanded }">
              <div v-if="!displayableChatHistory.length" class="empty-chat">
                <div class="empty-icon">💭</div>
                <p>暂无对话记录</p>
              </div>
              <div v-else class="chat-list">
                <div
                  v-for="(msg, index) in displayedMessages"
                  :key="index"
                  class="message-item"
                  :class="msg.role"
                >
                  <div class="message-avatar">
                    {{ msg.role === 'user' ? '👤' : '🤖' }}
                  </div>
                  <div class="message-content">
                    <div class="message-sender">
                      {{ msg.role === 'user' ? '我' : 'AI 咨询师' }}
                    </div>
                    <!-- 用户消息：纯文本 -->
                    <div class="message-bubble" v-if="msg.role === 'user'">
                      {{ msg.content }}
                    </div>
                    <!-- AI消息：渲染Markdown -->
                    <div
                      class="message-bubble markdown-message"
                      v-else
                      v-html="renderMessageMarkdown(msg.content)"
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ==================== 测评报告部分 ==================== -->
      <section
        class="assessment-section"
        v-if="activeSection === 'assessment' || activeSection === 'all' || !hasConsultation"
      >
        <div class="section-header" v-if="hasConsultation">
          <h2 class="section-title">
            <span class="section-icon">📊</span>
            心理测评报告
          </h2>
          <div class="section-meta">
            <span class="meta-tag">
              <span class="tag-icon">📄</span>
              {{ reportData.base_info.report_no }}
            </span>
            <span class="meta-tag">
              <span class="tag-icon">📅</span>
              {{ reportData.base_info.date }}
            </span>
          </div>
        </div>

        <!-- 报告概览 -->
        <div class="report-overview">
          <div class="card overview-card">
            <div class="overview-header">
              <div class="report-meta">
                <div class="meta-item">
                  <span class="meta-icon">📄</span>
                  <span class="meta-label">报告编号</span>
                  <span class="meta-value">{{ reportData.base_info.report_no || '--' }}</span>
                </div>
                <div class="meta-item">
                  <span class="meta-icon">📅</span>
                  <span class="meta-label">测评日期</span>
                  <span class="meta-value">{{ reportData.base_info.date || '--' }}</span>
                </div>
              </div>
              <div class="user-info">
                <div class="avatar">👤</div>
                <div class="user-details">
                  <h3 class="user-name">{{ reportData.base_info.user_name || '用户' }}</h3>
                  <p class="assessment-name">
                    {{ reportData.base_info.mode_name || '心理健康测评' }}
                  </p>
                </div>
              </div>
            </div>

            <!-- 风险等级卡片 -->
            <div class="risk-card" :class="riskClass">
              <div class="risk-content">
                <div class="risk-icon">
                  <span v-if="riskLevel === 'good'">😊</span>
                  <span v-else-if="riskLevel === 'moderate'">😐</span>
                  <span v-else>😟</span>
                </div>
                <div class="risk-details">
                  <h3 class="risk-title">{{ riskTitle }}</h3>
                  <p class="risk-summary">{{ reportData.core_result.summary_label }}</p>
                  <div class="risk-indicator">
                    <div class="indicator-bar">
                      <div class="indicator-fill" :style="{ width: riskPercentage + '%' }"></div>
                      <div class="indicator-marker" :style="{ left: riskPercentage + '%' }"></div>
                    </div>
                    <div class="indicator-labels">
                      <span>良好</span>
                      <span>中等</span>
                      <span>严重</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 详细内容 -->
        <div class="report-details">
          <!-- 左侧：图表和指标 -->
          <div class="report-left">
            <!-- 雷达图 -->
            <div class="card chart-card">
              <div class="card-header">
                <h3 class="card-title">
                  <span class="title-icon">📈</span>
                  心理维度雷达图
                </h3>
              </div>
              <div class="chart-container">
                <div
                  ref="chartRef"
                  class="chart"
                  v-if="reportData.charts?.radar_data?.length"
                ></div>
                <div v-else class="no-chart">
                  <div class="no-data-icon">📊</div>
                  <p>暂无图表数据</p>
                </div>
              </div>
              <div class="chart-legend" v-if="reportData.charts?.radar_data">
                <div
                  class="legend-item"
                  v-for="item in reportData.charts.radar_data"
                  :key="item.name"
                >
                  <div
                    class="legend-color"
                    :style="{ backgroundColor: getDimensionColor(item.value) }"
                  ></div>
                  <span class="legend-name">{{ item.name }}</span>
                  <span class="legend-value">{{ item.value.toFixed(1) }}</span>
                </div>
              </div>
            </div>

            <!-- 关键指标 -->
            <div class="card metrics-card">
              <div class="card-header">
                <h3 class="card-title">
                  <span class="title-icon">📊</span>
                  关键指标分析
                </h3>
              </div>
              <div class="metrics-list">
                <div class="metric-item" v-for="item in topDimensions" :key="item.name">
                  <div class="metric-header">
                    <span class="metric-name">{{ item.name }}</span>
                    <span class="metric-score" :class="getScoreClass(item.value)">
                      {{ item.value.toFixed(1) }}
                    </span>
                  </div>
                  <div class="metric-bar">
                    <div
                      class="bar-fill"
                      :style="{
                        width: Math.min((item.value / 5) * 100, 100) + '%',
                        backgroundColor: getDimensionColor(item.value),
                      }"
                    ></div>
                  </div>
                  <div class="metric-tag" :class="getRiskTagClass(item.value)">
                    {{ getRiskLevelText(item.value) }}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 右侧：详细建议 -->
          <div class="report-right">
            <div class="card advice-card">
              <div class="card-header">
                <h3 class="card-title">
                  <span class="title-icon">📝</span>
                  专业分析与建议
                </h3>
              </div>
              <div class="advice-body">
                <div
                  v-if="reportData.content?.advice_md"
                  class="markdown-content"
                  v-html="renderedMarkdown"
                ></div>
                <div v-else class="no-advice">
                  <p>暂无详细建议内容</p>
                </div>
              </div>
              <div class="advice-footer">
                <div class="disclaimer">
                  <span class="disclaimer-icon">⚠️</span>
                  <span class="disclaimer-text">
                    本报告仅供参考，不构成专业医疗建议。如有需要，请咨询专业心理医生。
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 底部操作栏 -->
      <div class="bottom-actions">
        <button class="action-btn secondary" @click="goBack">
          <span class="btn-icon">←</span>
          返回列表
        </button>
        <button class="action-btn primary" @click="startChat" v-if="!hasConsultation">
          <span class="btn-icon">💬</span>
          开始 AI 问诊
        </button>
        <button
          class="action-btn primary"
          @click="continueChat"
          v-else-if="consultationData?.status !== 'finished'"
        >
          <span class="btn-icon">💬</span>
          继续问诊
        </button>
        <button class="action-btn primary" @click="startNewChat" v-else>
          <span class="btn-icon">🔄</span>
          新一轮问诊
        </button>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { getReportDetail } from '@/api/assessment'
import { getConsultationDetail } from '@/api/history'

// ==================== 类型定义 ====================
interface ErrorInfo {
  title: string
  message: string
}

interface DimensionItem {
  name: string
  value: number
  fullMark: number
}

interface ReportData {
  base_info: {
    report_no: string
    date: string
    user_name: string
    mode_name: string
  }
  core_result: {
    risk_level: 'good' | 'moderate' | 'severe'
    risk_color: string
    summary_label: string
    score_interpretation: string
  }
  charts: {
    radar_data: DimensionItem[]
  }
  content: {
    advice_md: string
  }
  actions: {
    can_chat: boolean
    can_download: boolean
  }
}

interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
}

interface FilteredChatMessage {
  role: 'user' | 'assistant'
  content: string
}

interface ScoreChangeItem {
  dimension: string
  initial: string
  final: string
  change: number
}

type InitialScoresType = DimensionItem[] | Record<string, number> | null | undefined

interface ConsultationData {
  id: number
  report_id: number
  sequence_number: number
  diagnosis_summary: string | null
  initial_scores?: InitialScoresType
  final_scores?: Record<string, number> | null
  score_changes?: Record<string, number> | null
  initial_risk_level?: 'good' | 'moderate' | 'severe' | null
  final_risk_level?: 'good' | 'moderate' | 'severe' | null
  status: 'finished' | 'ongoing'
  updated_at: string
  chat_history: ChatMessage[]
}

// ==================== 路由和状态 ====================
const route = useRoute()
const router = useRouter()

const loading = ref(true)
const error = ref<ErrorInfo | null>(null)
const reportData = ref<ReportData | null>(null)
const consultationData = ref<ConsultationData | null>(null)
const activeSection = ref<'consultation' | 'assessment' | 'all'>('all')
const chatExpanded = ref(false)
const chartRef = ref<HTMLElement>()
const comparisonChartRef = ref<HTMLElement>()
let chartInstance: echarts.ECharts | null = null
let comparisonChartInstance: echarts.ECharts | null = null

// ==================== 辅助函数 ====================

/**
 * 【完全重写】清理诊断总结内容
 * 删除：备注、量化评估更新、SCL-90分数、JSON数据等
 */
/**
 * 【修复】清理诊断总结内容
 * 删除：量化评估更新、SCL-90分数、JSON数据等
 */
/**
 * 【修复版】清理诊断总结内容
 * 精确删除：量化评估章节、JSON数据、分数列表等
 * 不会误删有效内容
 */
const cleanDiagnosisSummary = (md: string | null | undefined): string => {
  if (!md) return ''

  let cleaned = md

  // ========== 1. 删除代码块（JSON等） ==========
  cleaned = cleaned.replace(/```json[\s\S]*?```/gi, '')
  cleaned = cleaned.replace(/```[\s\S]*?```/gi, '')

  // ========== 2. 删除独立的 JSON 对象 ==========
  // 匹配 { ... "scores" ... } 或 { ... "躯体化" ... } 格式的JSON
  cleaned = cleaned.replace(/\{[^{}]*"scores"[^{}]*\}/g, '')
  cleaned = cleaned.replace(/\{[^{}]*["']躯体化["'][^{}]*\}/g, '')
  // 匹配多行JSON对象
  cleaned = cleaned.replace(/\{\s*\n[\s\S]*?"躯体化"[\s\S]*?\n\s*\}/g, '')

  // ========== 3. 删除量化评估章节（精确匹配到下一章节） ==========
  // Markdown 标题格式: ### 量化评估 ... 直到下一个同级或更高级标题
  cleaned = cleaned.replace(/#{1,3}\s*量化评估[^]*?(?=\n#{1,3}\s|\n*$)/gi, '')

  // 中文序号格式: 五、量化评估 ... 直到下一个中文序号
  cleaned = cleaned.replace(
    /[一二三四五六七八九十]+[、.．]\s*量化评估[^]*?(?=\n[一二三四五六七八九十]+[、.．]|\n*$)/gi,
    '',
  )
  // ========== 4. 新增：删除从"以下删除"开始以及之后的所有内容 ==========
  // 匹配包含"以下删除"的行，删除该行及之后所有内容
  cleaned = cleaned.replace(/\n.*以下删除[\s\S]*/i, '')
  // 如果"以下删除"出现在开头
  cleaned = cleaned.replace(/^.*以下删除[\s\S]*/i, '')
  // 阿拉伯数字序号格式: 5. 量化评估 ... 直到下一个数字序号
  cleaned = cleaned.replace(/\d+[\.、．]\s*\**量化评估[^]*?(?=\n\d+[\.、．]|\n*$)/gi, '')

  // ========== 4. 删除独立的分数列表行 ==========
  const dimensions = [
    '躯体化',
    '强迫症状',
    '强迫',
    '人际关系敏感',
    '人际敏感',
    '抑郁',
    '焦虑',
    '敌对',
    '恐怖',
    '偏执',
    '精神病性',
    '其他',
    '总分',
    '总均分',
    '阳性项目数',
    '阳性症状均分',
    'somatization',
    'obsessive',
    'interpersonal',
    'depression',
    'anxiety',
    'hostility',
    'phobic',
    'paranoid',
    'psychoticism',
  ]
  const dimPattern = dimensions.join('|')

  // 匹配 "- 躯体化: 2.5" 或 "躯体化：2.5" 这样的独立行
  const dimRegex = new RegExp(`^\\s*[-*•]?\\s*(${dimPattern})\\s*[：:=→]\\s*[\\d.]+.*$`, 'gmi')
  cleaned = cleaned.replace(dimRegex, '')

  // ========== 5. 删除 SCL-90 相关的独立段落 ==========
  // 只删除以 SCL-90 开头的独立行或段落标题，不删除正文中的引用
  cleaned = cleaned.replace(/^#+\s*SCL-?90.*$/gm, '')
  cleaned = cleaned.replace(/^\*\*SCL-?90[^*]*\*\*\s*$/gm, '')
  cleaned = cleaned.replace(/^[-*]\s*SCL-?90.*$/gm, '')

  // ========== 6. 删除日期相关行 ==========
  cleaned = cleaned.replace(/^.*(?:就诊|诊断|问诊|评估)日期\s*[：:].*/gm, '')

  // ========== 7. 删除AI提示语 ==========
  cleaned = cleaned.replace(/^.*请根据对话内容.*$/gm, '')
  cleaned = cleaned.replace(/^.*以\s*JSON\s*格式.*$/gm, '')
  cleaned = cleaned.replace(/^.*输出如下数据.*$/gm, '')

  // ========== 8. 清理格式 ==========
  // 删除连续空行（保留最多两个换行）
  cleaned = cleaned.replace(/\n{3,}/g, '\n\n')
  // 删除只有空白符或列表符号的行
  cleaned = cleaned.replace(/^\s*[-*•]\s*$/gm, '')
  // 删除开头和结尾的空白
  cleaned = cleaned.trim()

  return cleaned
}

/**
 * 将初始分数统一转换为数组格式
 */
const normalizeInitialScores = (scores: InitialScoresType): DimensionItem[] => {
  if (!scores) return []

  if (Array.isArray(scores)) {
    return scores
  }

  if (typeof scores === 'object') {
    return Object.entries(scores).map(([name, value]) => ({
      name,
      value: typeof value === 'number' ? value : 0,
      fullMark: 5,
    }))
  }

  return []
}

/**
 * 从初始分数中获取某个维度的分数
 */
const getInitialScoreValue = (dimension: string): number | undefined => {
  const scores = consultationData.value?.initial_scores
  if (!scores) return undefined

  if (Array.isArray(scores)) {
    const item = scores.find((s) => s.name === dimension)
    return item?.value
  }

  if (typeof scores === 'object' && dimension in scores) {
    return (scores as Record<string, number>)[dimension]
  }

  return undefined
}

// ==================== 计算属性 ====================
const hasConsultation = computed(() => {
  return (
    !!consultationData.value &&
    (!!consultationData.value.chat_history?.length || !!consultationData.value.diagnosis_summary)
  )
})

const normalizedInitialScores = computed(() => {
  return normalizeInitialScores(consultationData.value?.initial_scores)
})

const hasScoreComparison = computed(() => {
  return (
    normalizedInitialScores.value.length > 0 &&
    consultationData.value?.final_scores &&
    Object.keys(consultationData.value.final_scores).length > 0
  )
})

const hasScoreChanges = computed(() => {
  return (
    consultationData.value?.score_changes &&
    Object.keys(consultationData.value.score_changes).length > 0
  )
})

const riskChanged = computed(() => {
  if (!consultationData.value) return false
  return consultationData.value.initial_risk_level !== consultationData.value.final_risk_level
})

const scoreChangesList = computed((): ScoreChangeItem[] => {
  const changes = consultationData.value?.score_changes
  if (!changes) return []

  return Object.entries(changes).map(([dimension, change]) => {
    const initialValue = getInitialScoreValue(dimension)
    const finalValue = consultationData.value?.final_scores?.[dimension]

    return {
      dimension,
      initial: initialValue !== undefined ? initialValue.toFixed(2) : '--',
      final: finalValue !== undefined ? finalValue.toFixed(2) : '--',
      change: typeof change === 'number' ? change : 0,
    }
  })
})

// 过滤后的对话历史（只保留用户和助手消息）
const filteredChatHistory = computed((): FilteredChatMessage[] => {
  const messages = consultationData.value?.chat_history || []
  return messages
    .filter(
      (msg): msg is ChatMessage & { role: 'user' | 'assistant' } =>
        msg.role === 'user' || msg.role === 'assistant',
    )
    .map((msg) => ({
      role: msg.role,
      content: msg.content,
    }))
})

// 可显示的对话历史：显示全部消息
const displayableChatHistory = computed((): FilteredChatMessage[] => {
  return filteredChatHistory.value
})

// 显示的消息（根据展开状态）
// 可选方案：收起时显示前2条作为预览
const displayedMessages = computed(() => {
  const messages = displayableChatHistory.value
  if (chatExpanded.value) return messages
  return messages.slice(0, 2) // 收起时显示前2条
})

// 风险等级相关
const riskLevel = computed(() => reportData.value?.core_result?.risk_level || 'good')

const riskTitle = computed(() => {
  const map: Record<string, string> = {
    good: '状态良好',
    moderate: '中度风险',
    severe: '高风险',
  }
  return map[riskLevel.value] || '状态未知'
})

const riskClass = computed(() => {
  const map: Record<string, string> = {
    good: 'risk-good',
    moderate: 'risk-moderate',
    severe: 'risk-severe',
  }
  return map[riskLevel.value] || 'risk-good'
})

const riskPercentage = computed(() => {
  const map: Record<string, number> = {
    good: 20,
    moderate: 55,
    severe: 85,
  }
  return map[riskLevel.value] || 20
})

const displayRiskLevel = computed(() => {
  if (hasConsultation.value && consultationData.value?.final_risk_level) {
    return consultationData.value.final_risk_level
  }
  return riskLevel.value
})

const displayRiskClass = computed(() => getRiskClass(displayRiskLevel.value))
const displayRiskLabel = computed(() => getRiskLabel(displayRiskLevel.value))

const topDimensions = computed(() => {
  if (!reportData.value?.charts?.radar_data) return []
  return [...reportData.value.charts.radar_data].sort((a, b) => b.value - a.value).slice(0, 5)
})

// Markdown渲染
const renderedMarkdown = computed(() => {
  const md = reportData.value?.content?.advice_md
  if (!md) return ''
  marked.setOptions({ breaks: true, gfm: true })
  const html = marked.parse(md) as string
  return DOMPurify.sanitize(html)
})
/**
 * 渲染消息内容的Markdown
 */
const renderMessageMarkdown = (content: string): string => {
  if (!content) return ''
  marked.setOptions({ breaks: true, gfm: true })
  const html = marked.parse(content) as string
  return DOMPurify.sanitize(html)
}
// 清理后的诊断总结
const cleanedDiagnosisSummaryHtml = computed(() => {
  const md = consultationData.value?.diagnosis_summary
  const cleanedMd = cleanDiagnosisSummary(md)
  if (!cleanedMd) return ''

  marked.setOptions({ breaks: true, gfm: true })
  const html = marked.parse(cleanedMd) as string
  return DOMPurify.sanitize(html)
})

// ==================== 生命周期 ====================
onMounted(async () => {
  await fetchAllData()
})

onBeforeUnmount(() => {
  if (chartInstance) chartInstance.dispose()
  if (comparisonChartInstance) comparisonChartInstance.dispose()
  window.removeEventListener('resize', handleResize)
})

watch(activeSection, (newVal) => {
  nextTick(() => {
    if (newVal === 'assessment' || newVal === 'all') {
      initChart()
    }
    if ((newVal === 'consultation' || newVal === 'all') && hasScoreComparison.value) {
      initComparisonChart()
    }
  })
})

// ==================== 数据获取 ====================
const fetchAllData = async () => {
  const reportId = route.params.reportId as string
  const consultationId = route.query.consultationId as string
  const uid = parseInt(localStorage.getItem('uid') || '0')

  if (!reportId || !uid) {
    error.value = {
      title: '参数错误',
      message: '报告ID或用户信息缺失',
    }
    loading.value = false
    return
  }

  try {
    loading.value = true
    error.value = null

    const reportRes = await getReportDetail(reportId, uid)

    if (reportRes.code === 200) {
      reportData.value = reportRes.data
    } else {
      throw new Error(reportRes.msg || '获取测评报告失败')
    }

    if (consultationId) {
      try {
        const consultRes = await getConsultationDetail(consultationId)
        if (consultRes.code === 200) {
          consultationData.value = consultRes.data as ConsultationData
        }
      } catch (err) {
        console.warn('获取问诊详情失败，但不影响测评报告展示', err)
      }
    }

    nextTick(() => {
      initChart()
      if (hasScoreComparison.value) {
        initComparisonChart()
      }
    })
  } catch (err: unknown) {
    error.value = {
      title: '加载失败',
      message: err instanceof Error ? err.message : '获取报告数据失败',
    }
    console.error('获取报告失败:', err)
  } finally {
    loading.value = false
  }
}

// ==================== 图表初始化 ====================
const initChart = () => {
  if (!chartRef.value || !reportData.value?.charts?.radar_data) return

  if (chartInstance) chartInstance.dispose()

  chartInstance = echarts.init(chartRef.value)

  const chartData = reportData.value.charts.radar_data
  const indicator = chartData.map((item) => ({
    name: item.name,
    max: item.fullMark || 5,
  }))
  const values = chartData.map((item) => item.value)

  const option: echarts.EChartsOption = {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'item', formatter: '{b}: {c}分' },
    radar: {
      indicator,
      shape: 'circle',
      splitNumber: 4,
      axisName: { color: '#546e7a', fontSize: 12 },
      splitLine: { lineStyle: { color: 'rgba(0, 137, 123, 0.1)' } },
      splitArea: { areaStyle: { color: ['rgba(0, 137, 123, 0.02)', 'rgba(0, 137, 123, 0.05)'] } },
      axisLine: { lineStyle: { color: 'rgba(0, 137, 123, 0.2)' } },
    },
    series: [
      {
        type: 'radar',
        data: [
          {
            value: values,
            name: '心理维度',
            itemStyle: { color: '#00897b' },
            areaStyle: {
              color: {
                type: 'radial',
                x: 0.5,
                y: 0.5,
                r: 0.5,
                colorStops: [
                  { offset: 0, color: 'rgba(0, 137, 123, 0.3)' },
                  { offset: 1, color: 'rgba(0, 137, 123, 0.1)' },
                ],
              },
            },
            lineStyle: { width: 2, color: '#00897b' },
            symbol: 'circle',
            symbolSize: 8,
            label: {
              show: true,
              formatter: '{c}',
              color: '#00897b',
              fontSize: 11,
              fontWeight: 'bold',
            },
          },
        ],
      },
    ],
  }

  chartInstance.setOption(option)
  window.addEventListener('resize', handleResize)
}

const initComparisonChart = () => {
  if (!comparisonChartRef.value || !consultationData.value) return

  const initialScores = normalizedInitialScores.value
  const finalScores = consultationData.value.final_scores

  if (!initialScores.length || !finalScores) return

  if (comparisonChartInstance) comparisonChartInstance.dispose()

  comparisonChartInstance = echarts.init(comparisonChartRef.value)

  const indicator = initialScores.map((item) => ({
    name: item.name,
    max: item.fullMark || 5,
  }))

  const initialValues = initialScores.map((item) => item.value)
  const finalValues = initialScores.map((item) => finalScores[item.name] ?? item.value)

  const option: echarts.EChartsOption = {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'item' },
    legend: {
      data: ['上次评估', 'AI修正'],
      bottom: 10,
      textStyle: { color: '#546e7a', fontSize: 12 },
    },
    radar: {
      indicator,
      shape: 'circle',
      splitNumber: 4,
      axisName: { color: '#546e7a', fontSize: 11 },
      splitLine: { lineStyle: { color: 'rgba(0, 137, 123, 0.1)' } },
      splitArea: { areaStyle: { color: ['rgba(0, 137, 123, 0.02)', 'rgba(0, 137, 123, 0.05)'] } },
      axisLine: { lineStyle: { color: 'rgba(0, 137, 123, 0.2)' } },
    },
    series: [
      {
        type: 'radar',
        data: [
          {
            value: initialValues,
            name: '上次评估',
            itemStyle: { color: '#90a4ae' },
            areaStyle: { color: 'rgba(144, 164, 174, 0.2)' },
            lineStyle: { width: 2, color: '#90a4ae', type: 'dashed' },
            symbol: 'circle',
            symbolSize: 6,
          },
          {
            value: finalValues,
            name: 'AI修正',
            itemStyle: { color: '#00897b' },
            areaStyle: { color: 'rgba(0, 137, 123, 0.25)' },
            lineStyle: { width: 2, color: '#00897b' },
            symbol: 'circle',
            symbolSize: 8,
            label: {
              show: true,
              formatter: '{c}',
              color: '#00897b',
              fontSize: 10,
              fontWeight: 'bold',
            },
          },
        ],
      },
    ],
  }

  comparisonChartInstance.setOption(option)
}

const handleResize = () => {
  chartInstance?.resize()
  comparisonChartInstance?.resize()
}

// ==================== 辅助方法 ====================
const getDimensionColor = (value: number): string => {
  if (value <= 2) return '#4caf50'
  if (value <= 3) return '#ff9800'
  return '#f44336'
}

const getScoreClass = (value: number): string => {
  if (value <= 2) return 'score-low'
  if (value <= 3) return 'score-medium'
  return 'score-high'
}

const getRiskLevelText = (value: number): string => {
  if (value <= 2) return '良好'
  if (value <= 3) return '中等'
  return '较高'
}

const getRiskTagClass = (value: number): string => {
  if (value <= 2) return 'tag-good'
  if (value <= 3) return 'tag-moderate'
  return 'tag-severe'
}

const getRiskClass = (level: string | null | undefined): string => {
  const map: Record<string, string> = {
    good: 'risk-good',
    moderate: 'risk-moderate',
    severe: 'risk-severe',
  }
  return map[level || 'good'] || 'risk-good'
}

const getRiskLabel = (level: string | null | undefined): string => {
  const map: Record<string, string> = {
    good: '良好',
    moderate: '中等',
    severe: '高风险',
  }
  return map[level || 'good'] || '良好'
}

const getRiskEmoji = (level: string | null | undefined): string => {
  const map: Record<string, string> = {
    good: '😊',
    moderate: '😐',
    severe: '😟',
  }
  return map[level || 'good'] || '😊'
}

const getChangeClass = (change: number): string => {
  if (change > 0) return 'change-up'
  if (change < 0) return 'change-down'
  return 'change-none'
}

// ==================== 导航方法 ====================
const goHome = () => router.push('/home')
const goBack = () => router.back()
const retry = () => fetchAllData()

const startChat = () => {
  const reportId = route.params.reportId
  router.push({ name: 'consultationChat', params: { reportId } })
}

const continueChat = () => {
  const reportId = route.params.reportId
  router.push({ name: 'consultationChat', params: { reportId } })
}

const startNewChat = () => {
  const reportId = route.params.reportId
  router.push({ name: 'consultationChat', params: { reportId }, query: { newSession: 'true' } })
}
</script>

<style scoped>
/* 样式部分保持不变，与之前相同 */
/* ============ 基础布局 ============ */
.report-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8f9ff 0%, #f0f7ff 50%, #e8f5e9 100%);
  position: relative;
}

/* ============ 背景装饰 ============ */
.background-decoration {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
}

.bubble {
  position: absolute;
  border-radius: 50%;
  background: rgba(0, 137, 123, 0.05);
  animation: float 20s infinite ease-in-out;
}

.bubble-1 {
  width: 350px;
  height: 350px;
  top: -100px;
  right: -80px;
}
.bubble-2 {
  width: 250px;
  height: 250px;
  bottom: 10%;
  left: -60px;
  animation-delay: -7s;
}
.bubble-3 {
  width: 180px;
  height: 180px;
  top: 40%;
  right: 15%;
  animation-delay: -14s;
}

.floating-icon {
  position: absolute;
  font-size: 28px;
  opacity: 0.12;
  animation: iconFloat 18s infinite ease-in-out;
}

.icon-1 {
  top: 12%;
  left: 8%;
}
.icon-2 {
  top: 55%;
  right: 6%;
  animation-delay: -6s;
}
.icon-3 {
  bottom: 18%;
  left: 12%;
  animation-delay: -12s;
}

@keyframes float {
  0%,
  100% {
    transform: translateY(0) scale(1);
  }
  50% {
    transform: translateY(-25px) scale(1.03);
  }
}

@keyframes iconFloat {
  0%,
  100% {
    transform: translateY(0) rotate(0deg);
  }
  50% {
    transform: translateY(-15px) rotate(10deg);
  }
}

/* ============ 页面头部 ============ */
.page-header {
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(0, 137, 123, 0.08);
  padding: 16px 30px;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: transform 0.3s;
}

.logo-section:hover {
  transform: scale(1.05);
}
.logo-icon {
  font-size: 32px;
  animation: pulse 3s ease-in-out infinite;
}

@keyframes pulse {
  0%,
  100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}

.site-title {
  color: #00897b;
  font-size: 18px;
  margin: 0;
  font-weight: 700;
}
.site-subtitle {
  color: #90a4ae;
  font-size: 11px;
  margin: 2px 0 0;
  letter-spacing: 1px;
}
.header-center {
  text-align: center;
  flex: 1;
}

.page-title {
  color: #263238;
  font-size: 22px;
  margin: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  font-weight: 700;
}

.title-icon {
  font-size: 26px;
}

.title-badge {
  padding: 5px 14px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  color: white;
}

.title-badge.risk-good {
  background: linear-gradient(135deg, #4caf50, #66bb6a);
}
.title-badge.risk-moderate {
  background: linear-gradient(135deg, #ff9800, #ffb74d);
}
.title-badge.risk-severe {
  background: linear-gradient(135deg, #f44336, #ef5350);
}

.page-subtitle {
  color: #90a4ae;
  font-size: 13px;
  margin: 6px 0 0;
}
.action-buttons {
  display: flex;
  gap: 12px;
}

.action-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.chat-btn {
  background: linear-gradient(135deg, #00897b, #26a69a);
  color: white;
}
.back-btn {
  background: rgba(0, 137, 123, 0.1);
  color: #00897b;
}
.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12);
}

/* ============ 主内容区域 ============ */
.main-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 25px 20px 40px;
  position: relative;
  z-index: 1;
}

/* ============ 报告标签页 ============ */
.report-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 25px;
  padding: 6px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  width: fit-content;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border: none;
  background: transparent;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  color: #78909c;
  cursor: pointer;
  transition: all 0.3s;
}

.tab-btn:hover {
  background: rgba(0, 137, 123, 0.08);
  color: #00897b;
}
.tab-btn.active {
  background: white;
  color: #00897b;
  box-shadow: 0 4px 15px rgba(0, 137, 123, 0.15);
}
.tab-icon {
  font-size: 18px;
}

/* ============ 章节样式 ============ */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid rgba(0, 137, 123, 0.1);
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 20px;
  font-weight: 700;
  color: #263238;
  margin: 0;
}

.section-icon {
  font-size: 24px;
}
.section-meta {
  display: flex;
  gap: 15px;
}

.meta-tag {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  background: rgba(0, 137, 123, 0.08);
  border-radius: 20px;
  font-size: 13px;
  color: #546e7a;
}

.meta-tag.status-tag.finished {
  background: rgba(76, 175, 80, 0.1);
  color: #4caf50;
}
.meta-tag.status-tag.ongoing {
  background: rgba(255, 152, 0, 0.1);
  color: #ff9800;
}
.tag-icon {
  font-size: 14px;
}

/* ============ 卡片基础样式 ============ */
.card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 137, 123, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.8);
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid rgba(0, 137, 123, 0.08);
}

.card-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 17px;
  font-weight: 700;
  color: #263238;
  margin: 0;
}

.title-icon {
  font-size: 20px;
}

/* ============ 问诊部分布局 ============ */
.consultation-section {
  margin-bottom: 35px;
}

.consultation-content {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.consultation-content .full-width {
  grid-column: 1 / -1;
}

/* ============ 风险等级变化卡片 ============ */
.risk-change-card {
  grid-column: 1 / -1;
}
.risk-change-body {
  padding: 24px;
}

.risk-comparison {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 30px;
  padding: 20px;
  background: linear-gradient(135deg, rgba(0, 137, 123, 0.03), rgba(38, 166, 154, 0.02));
  border-radius: 16px;
}

.risk-item {
  text-align: center;
}
.risk-label {
  font-size: 13px;
  color: #78909c;
  margin-bottom: 10px;
  font-weight: 600;
}

.risk-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border-radius: 30px;
  font-weight: 700;
}

.risk-badge.risk-good {
  background: linear-gradient(135deg, rgba(76, 175, 80, 0.15), rgba(102, 187, 106, 0.1));
  color: #4caf50;
}
.risk-badge.risk-moderate {
  background: linear-gradient(135deg, rgba(255, 152, 0, 0.15), rgba(255, 183, 77, 0.1));
  color: #ff9800;
}
.risk-badge.risk-severe {
  background: linear-gradient(135deg, rgba(244, 67, 54, 0.15), rgba(239, 83, 80, 0.1));
  color: #f44336;
}

.risk-emoji {
  font-size: 24px;
}
.risk-text {
  font-size: 16px;
}
.risk-arrow {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}
.arrow-icon {
  font-size: 28px;
  color: #00897b;
  font-weight: bold;
}
.arrow-label {
  font-size: 11px;
  color: #90a4ae;
  font-weight: 600;
}

.risk-note {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin-top: 16px;
  padding: 12px 16px;
  background: rgba(0, 137, 123, 0.06);
  border-radius: 10px;
  border-left: 3px solid #00897b;
}

.note-icon {
  font-size: 16px;
  flex-shrink: 0;
}
.note-text {
  font-size: 13px;
  color: #546e7a;
  line-height: 1.5;
}

/* ============ 分数对比雷达图 ============ */
.comparison-chart-card .chart-container {
  height: 320px;
  padding: 0 20px;
}
.comparison-chart-card .chart {
  width: 100%;
  height: 100%;
}
.legend-inline {
  display: flex;
  gap: 20px;
}
.legend-inline .legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #546e7a;
}
.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}
.legend-dot.initial {
  background: #90a4ae;
  border: 2px dashed #78909c;
}
.legend-dot.final {
  background: #00897b;
}

/* ============ 分数变化详情 ============ */
.score-changes-body {
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 350px;
  overflow-y: auto;
}

.change-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 18px;
  background: rgba(0, 137, 123, 0.03);
  border: 1px solid rgba(0, 137, 123, 0.08);
  border-radius: 12px;
  transition: all 0.3s;
}

.change-item:hover {
  transform: translateX(4px);
  box-shadow: 0 4px 15px rgba(0, 137, 123, 0.1);
}
.change-dimension {
  font-size: 14px;
  font-weight: 600;
  color: #263238;
  flex: 1;
}
.change-scores {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}
.score-initial {
  color: #90a4ae;
  font-weight: 500;
}
.score-arrow {
  color: #b0bec5;
  font-size: 12px;
}
.score-final {
  color: #00897b;
  font-weight: 700;
}

.change-value {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 700;
  min-width: 80px;
  justify-content: center;
}

.change-value.change-up {
  background: rgba(244, 67, 54, 0.1);
  color: #f44336;
}
.change-value.change-down {
  background: rgba(76, 175, 80, 0.1);
  color: #4caf50;
}
.change-value.change-none {
  background: rgba(158, 158, 158, 0.1);
  color: #9e9e9e;
}
.change-icon {
  font-size: 14px;
}

/* ============ AI诊断总结卡片 ============ */
.diagnosis-card,
.chat-card {
  height: fit-content;
}

.ai-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  background: linear-gradient(135deg, #e8f5e9, #e0f7fa);
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  color: #00897b;
}

.diagnosis-body {
  padding: 24px;
}

.diagnosis-markdown {
  padding: 20px;
  background: linear-gradient(135deg, rgba(0, 137, 123, 0.04), rgba(38, 166, 154, 0.02));
  border-radius: 12px;
  border-left: 4px solid #00897b;
}

.no-diagnosis,
.no-chart,
.no-advice,
.empty-chat {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: #b0bec5;
}

.no-data-icon,
.empty-icon {
  font-size: 48px;
  margin-bottom: 12px;
  opacity: 0.5;
}

/* ============ 对话卡片 ============ */
.chat-meta {
  display: flex;
  align-items: center;
  gap: 15px;
}
.chat-count {
  font-size: 13px;
  color: #90a4ae;
  font-weight: 500;
}

.expand-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: rgba(0, 137, 123, 0.08);
  border: none;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  color: #00897b;
  cursor: pointer;
  transition: all 0.3s;
}

.expand-btn:hover {
  background: rgba(0, 137, 123, 0.15);
}

.chat-body {
  padding: 20px 24px;
  max-height: 350px;
  overflow: hidden;
  transition: max-height 0.4s ease;
}

.chat-body.expanded {
  max-height: 600px;
  overflow-y: auto;
}
.chat-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.message-item {
  display: flex;
  gap: 12px;
  max-width: 90%;
}
.message-item.user {
  flex-direction: row-reverse;
  margin-left: auto;
}

.message-avatar {
  width: 38px;
  height: 38px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}

.message-item.assistant .message-avatar {
  background: white;
  border: 1px solid #e0f2f1;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}
.message-item.user .message-avatar {
  background: linear-gradient(135deg, #00897b, #26a69a);
}
.message-content {
  flex: 1;
  min-width: 0;
}
.message-sender {
  font-size: 12px;
  font-weight: 600;
  color: #78909c;
  margin-bottom: 4px;
}
.message-item.user .message-sender {
  text-align: right;
}

.message-bubble {
  padding: 12px 16px;
  border-radius: 14px;
  font-size: 14px;
  line-height: 1.6;
  color: #37474f;
}

.message-item.assistant .message-bubble {
  background: white;
  border: 1px solid rgba(0, 137, 123, 0.1);
  border-top-left-radius: 4px;
}
.message-item.user .message-bubble {
  background: linear-gradient(135deg, #e0f2f1, #e8f5e9);
  border-top-right-radius: 4px;
}

/* ============ 测评报告部分 ============ */
.assessment-section {
  margin-bottom: 30px;
}
.report-overview {
  margin-bottom: 25px;
}
.overview-card {
  padding: 28px;
}

.overview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid rgba(0, 137, 123, 0.1);
}

.report-meta {
  display: flex;
  gap: 30px;
}
.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
}
.meta-icon {
  font-size: 18px;
}
.meta-label {
  color: #90a4ae;
  font-size: 13px;
}
.meta-value {
  color: #263238;
  font-size: 15px;
  font-weight: 600;
}
.user-info {
  display: flex;
  align-items: center;
  gap: 14px;
}

.avatar {
  width: 52px;
  height: 52px;
  background: linear-gradient(135deg, #00897b, #26a69a);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
  box-shadow: 0 4px 15px rgba(0, 137, 123, 0.25);
}

.user-name {
  font-size: 18px;
  font-weight: 700;
  color: #263238;
  margin: 0 0 4px;
}
.assessment-name {
  font-size: 13px;
  color: #90a4ae;
  margin: 0;
}

/* 风险卡片 */
.risk-card {
  border-radius: 16px;
  padding: 24px;
  transition: all 0.3s;
}
.risk-card.risk-good {
  background: linear-gradient(135deg, rgba(76, 175, 80, 0.1), rgba(102, 187, 106, 0.05));
  border: 1px solid rgba(76, 175, 80, 0.2);
}
.risk-card.risk-moderate {
  background: linear-gradient(135deg, rgba(255, 152, 0, 0.1), rgba(255, 183, 77, 0.05));
  border: 1px solid rgba(255, 152, 0, 0.2);
}
.risk-card.risk-severe {
  background: linear-gradient(135deg, rgba(244, 67, 54, 0.1), rgba(239, 83, 80, 0.05));
  border: 1px solid rgba(244, 67, 54, 0.2);
}
.risk-content {
  display: flex;
  align-items: center;
  gap: 24px;
}

.risk-icon {
  width: 80px;
  height: 80px;
  background: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 44px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
}

.risk-details {
  flex: 1;
}
.risk-title {
  font-size: 24px;
  font-weight: 700;
  color: #263238;
  margin: 0 0 10px;
}
.risk-summary {
  font-size: 14px;
  color: #546e7a;
  line-height: 1.6;
  margin: 0 0 18px;
}
.risk-indicator {
  background: rgba(255, 255, 255, 0.85);
  border-radius: 12px;
  padding: 16px;
}

.indicator-bar {
  height: 10px;
  background: linear-gradient(to right, #4caf50, #ff9800, #f44336);
  border-radius: 5px;
  position: relative;
  margin-bottom: 10px;
}

.indicator-fill {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  background: rgba(255, 255, 255, 0.35);
  border-radius: 5px;
  transition: width 1s ease;
}

.indicator-marker {
  position: absolute;
  top: -4px;
  width: 18px;
  height: 18px;
  background: white;
  border: 3px solid #263238;
  border-radius: 50%;
  transform: translateX(-50%);
  transition: left 1s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.indicator-labels {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #78909c;
  font-weight: 600;
}

/* 详细内容布局 */
.report-details {
  display: flex;
  gap: 25px;
}
.report-left {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 25px;
}
.report-right {
  flex: 1.2;
}

/* 图表卡片 */
.chart-card {
  padding-bottom: 20px;
}
.chart-container {
  height: 280px;
  padding: 0 20px;
}
.chart {
  width: 100%;
  height: 100%;
}

.chart-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 15px 24px;
  border-top: 1px solid rgba(0, 137, 123, 0.08);
}

.chart-legend .legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: rgba(0, 137, 123, 0.04);
  border-radius: 20px;
  font-size: 12px;
}

.legend-color {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}
.legend-name {
  color: #546e7a;
  font-weight: 500;
}
.legend-value {
  color: #00897b;
  font-weight: 700;
}

/* 指标卡片 */
.metrics-card {
  padding-bottom: 10px;
}
.metrics-list {
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.metric-item {
  padding: 16px;
  background: rgba(0, 137, 123, 0.03);
  border: 1px solid rgba(0, 137, 123, 0.08);
  border-radius: 14px;
  transition: all 0.3s;
}

.metric-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 137, 123, 0.1);
}
.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.metric-name {
  font-size: 14px;
  font-weight: 600;
  color: #263238;
}
.metric-score {
  font-size: 20px;
  font-weight: 700;
}
.metric-score.score-low {
  color: #4caf50;
}
.metric-score.score-medium {
  color: #ff9800;
}
.metric-score.score-high {
  color: #f44336;
}

.metric-bar {
  height: 8px;
  background: rgba(0, 137, 123, 0.1);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 10px;
}

.bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.8s ease;
}

.metric-tag {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  color: white;
}

.metric-tag.tag-good {
  background: #4caf50;
}
.metric-tag.tag-moderate {
  background: #ff9800;
}
.metric-tag.tag-severe {
  background: #f44336;
}

/* 建议卡片 */
.advice-card {
  height: fit-content;
}
.advice-body {
  padding: 24px;
  max-height: 500px;
  overflow-y: auto;
}

/* Markdown 样式 */
.markdown-content {
  color: #37474f;
  line-height: 1.8;
  font-size: 15px;
}
.markdown-content :deep(h1) {
  color: #00897b;
  font-size: 22px;
  margin: 25px 0 15px;
  padding-bottom: 10px;
  border-bottom: 2px solid rgba(0, 137, 123, 0.1);
}
.markdown-content :deep(h2) {
  color: #263238;
  font-size: 18px;
  margin: 20px 0 12px;
  font-weight: 700;
}
.markdown-content :deep(h3) {
  color: #00897b;
  font-size: 16px;
  margin: 18px 0 12px;
  padding-left: 12px;
  border-left: 4px solid #00897b;
}
.markdown-content :deep(p) {
  margin: 12px 0;
  color: #455a64;
}
.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  margin: 12px 0;
  padding-left: 24px;
}
.markdown-content :deep(li) {
  margin: 6px 0;
  color: #455a64;
}
.markdown-content :deep(strong) {
  color: #00897b;
  font-weight: 700;
}
.markdown-content :deep(blockquote) {
  border-left: 4px solid #00897b;
  padding: 12px 18px;
  margin: 18px 0;
  background: rgba(0, 137, 123, 0.05);
  border-radius: 0 8px 8px 0;
}

.advice-footer {
  padding: 16px 24px;
  border-top: 1px solid rgba(0, 137, 123, 0.08);
}

.disclaimer {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 12px 16px;
  background: rgba(255, 152, 0, 0.08);
  border-radius: 10px;
  border-left: 3px solid #ff9800;
}

.disclaimer-icon {
  font-size: 16px;
  flex-shrink: 0;
}
.disclaimer-text {
  color: #78909c;
  font-size: 12px;
  line-height: 1.5;
}

/* ============ 底部操作栏 ============ */
.bottom-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  padding: 30px 0;
  margin-top: 20px;
}
.bottom-actions .action-btn {
  padding: 14px 32px;
  font-size: 15px;
  border-radius: 14px;
}
.bottom-actions .action-btn.primary {
  background: linear-gradient(135deg, #00897b, #26a69a);
  color: white;
  box-shadow: 0 6px 25px rgba(0, 137, 123, 0.3);
}
.bottom-actions .action-btn.secondary {
  background: white;
  color: #546e7a;
  border: 1px solid rgba(0, 137, 123, 0.2);
}
.bottom-actions .action-btn:hover {
  transform: translateY(-3px);
}

/* ============ 加载与错误状态 ============ */
.loading-state,
.error-state {
  position: fixed;
  inset: 0;
  background: linear-gradient(135deg, #f8f9ff 0%, #f0f7ff 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.loading-content,
.error-content {
  text-align: center;
  max-width: 400px;
  padding: 50px;
  background: white;
  border-radius: 24px;
  box-shadow: 0 25px 80px rgba(0, 137, 123, 0.12);
}

.loading-animation {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-bottom: 25px;
}

.loading-circle {
  width: 16px;
  height: 16px;
  background: linear-gradient(135deg, #00897b, #26a69a);
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out;
}

.loading-circle:nth-child(1) {
  animation-delay: 0s;
}
.loading-circle:nth-child(2) {
  animation-delay: 0.2s;
}
.loading-circle:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes bounce {
  0%,
  80%,
  100% {
    transform: scale(0);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.loading-title {
  font-size: 20px;
  font-weight: 600;
  color: #263238;
  margin: 0 0 8px;
}
.loading-subtitle {
  font-size: 14px;
  color: #90a4ae;
  margin: 0;
}
.error-icon {
  font-size: 64px;
  margin-bottom: 20px;
}
.error-title {
  font-size: 22px;
  font-weight: 600;
  color: #263238;
  margin: 0 0 10px;
}
.error-message {
  font-size: 14px;
  color: #78909c;
  margin: 0 0 25px;
  line-height: 1.5;
}
.error-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
}

.error-btn {
  padding: 12px 28px;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.error-btn.primary {
  background: linear-gradient(135deg, #00897b, #26a69a);
  color: white;
}
.error-btn.secondary {
  background: rgba(0, 137, 123, 0.1);
  color: #00897b;
}
.error-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
}

/* ============ 响应式 ============ */
@media (max-width: 1200px) {
  .consultation-content {
    grid-template-columns: 1fr;
  }
  .report-details {
    flex-direction: column;
  }
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  .overview-header {
    flex-direction: column;
    gap: 20px;
    align-items: flex-start;
  }
  .report-meta {
    flex-direction: column;
    gap: 12px;
  }
  .risk-content {
    flex-direction: column;
    text-align: center;
  }
  .section-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  .report-tabs {
    width: 100%;
    overflow-x: auto;
  }
  .tab-btn {
    flex: 1;
    justify-content: center;
    padding: 10px 16px;
  }
  .risk-comparison {
    flex-direction: column;
    gap: 20px;
  }
  .risk-arrow {
    transform: rotate(90deg);
  }
  .bottom-actions {
    flex-direction: column;
    padding: 20px;
  }
  .bottom-actions .action-btn {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .page-header {
    padding: 12px 16px;
  }
  .main-content {
    padding: 20px 16px;
  }
  .page-title {
    font-size: 18px;
  }
  .btn-text {
    display: none;
  }
  .card-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  .chart-container {
    height: 240px;
  }
  .comparison-chart-card .chart-container {
    height: 280px;
  }
}
/* ============ 消息气泡中的Markdown样式 ============ */
.message-bubble.markdown-message {
  padding: 12px 16px;
}

.message-bubble.markdown-message :deep(p) {
  margin: 0 0 8px;
  line-height: 1.6;
}

.message-bubble.markdown-message :deep(p:last-child) {
  margin-bottom: 0;
}

.message-bubble.markdown-message :deep(h1),
.message-bubble.markdown-message :deep(h2),
.message-bubble.markdown-message :deep(h3),
.message-bubble.markdown-message :deep(h4) {
  margin: 12px 0 8px;
  font-weight: 600;
  color: #263238;
}

.message-bubble.markdown-message :deep(h1) {
  font-size: 18px;
}

.message-bubble.markdown-message :deep(h2) {
  font-size: 16px;
}

.message-bubble.markdown-message :deep(h3) {
  font-size: 15px;
  color: #00897b;
}

.message-bubble.markdown-message :deep(ul),
.message-bubble.markdown-message :deep(ol) {
  margin: 8px 0;
  padding-left: 20px;
}

.message-bubble.markdown-message :deep(li) {
  margin: 4px 0;
  line-height: 1.5;
}

.message-bubble.markdown-message :deep(strong) {
  color: #00897b;
  font-weight: 600;
}

.message-bubble.markdown-message :deep(em) {
  font-style: italic;
  color: #546e7a;
}

.message-bubble.markdown-message :deep(blockquote) {
  margin: 8px 0;
  padding: 8px 12px;
  border-left: 3px solid #00897b;
  background: rgba(0, 137, 123, 0.05);
  border-radius: 0 6px 6px 0;
}

.message-bubble.markdown-message :deep(code) {
  background: rgba(0, 137, 123, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
  font-family: 'Consolas', monospace;
}

.message-bubble.markdown-message :deep(pre) {
  background: rgba(0, 137, 123, 0.08);
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 8px 0;
}

.message-bubble.markdown-message :deep(pre code) {
  background: transparent;
  padding: 0;
}

.message-bubble.markdown-message :deep(hr) {
  border: none;
  height: 1px;
  background: rgba(0, 137, 123, 0.15);
  margin: 12px 0;
}

.message-bubble.markdown-message :deep(a) {
  color: #00897b;
  text-decoration: underline;
}

.message-bubble.markdown-message :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 8px 0;
  font-size: 13px;
}

.message-bubble.markdown-message :deep(th),
.message-bubble.markdown-message :deep(td) {
  padding: 6px 10px;
  border: 1px solid rgba(0, 137, 123, 0.15);
  text-align: left;
}

.message-bubble.markdown-message :deep(th) {
  background: rgba(0, 137, 123, 0.08);
  font-weight: 600;
}
</style>
