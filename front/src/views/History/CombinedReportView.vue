<!-- views/Report/CombinedReportView.vue -->
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
            <span class="title-badge" :class="riskClass" v-if="reportData">
              {{ riskLabel }}
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
            <span class="meta-tag">
              <span class="tag-icon">📅</span>
              {{ consultationData?.date }}
            </span>
            <span class="meta-tag">
              <span class="tag-icon">💬</span>
              {{ consultationData?.chat_history?.length || 0 }} 轮对话
            </span>
          </div>
        </div>

        <div class="consultation-content">
          <!-- AI诊断建议卡片 -->
          <div class="card diagnosis-card">
            <div class="card-header">
              <h3 class="card-title">
                <span class="title-icon">📝</span>
                AI 诊断建议
              </h3>
              <div class="ai-badge">
                <span class="badge-icon">✨</span>
                <span class="badge-text">AI 智能分析</span>
              </div>
            </div>
            <div class="diagnosis-body">
              <div v-if="consultationData?.diagnosis_report" class="diagnosis-text">
                {{ consultationData.diagnosis_report }}
              </div>
              <div v-else class="no-diagnosis">
                <div class="no-data-icon">💭</div>
                <p>本次问诊暂无总结建议</p>
              </div>
            </div>
          </div>

          <!-- 对话回顾卡片 -->
          <div class="card chat-card">
            <div class="card-header">
              <h3 class="card-title">
                <span class="title-icon">💬</span>
                对话回顾
              </h3>
              <button class="expand-btn" @click="chatExpanded = !chatExpanded">
                {{ chatExpanded ? '收起' : '展开全部' }}
                <span class="expand-icon">{{ chatExpanded ? '↑' : '↓' }}</span>
              </button>
            </div>
            <div class="chat-body" :class="{ expanded: chatExpanded }">
              <div v-if="!consultationData?.chat_history?.length" class="empty-chat">
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
                    <div class="message-bubble">
                      {{ msg.content }}
                    </div>
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
        <button class="action-btn primary" @click="continueChat" v-else>
          <span class="btn-icon">💬</span>
          继续问诊
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

// 类型定义
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

// 后端返回的聊天消息类型（可能包含 system 角色）
interface ApiChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
}

// 前端展示的聊天消息类型（只包含 user 和 assistant 角色）
interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

// 后端返回的问诊数据接口
interface ApiConsultationData {
  id?: number
  sequence_number?: number
  date: string
  chat_history: ApiChatMessage[]
  diagnosis_report: string
  report_id?: number
}

// 前端使用的问诊数据接口（过滤掉 system 消息）
interface ConsultationData {
  date: string
  diagnosis_report: string
  chat_history: ChatMessage[]
}

const route = useRoute()
const router = useRouter()

// 状态
const loading = ref(true)
const error = ref<ErrorInfo | null>(null)
const reportData = ref<ReportData | null>(null)
const consultationData = ref<ConsultationData | null>(null)
const activeSection = ref<'consultation' | 'assessment' | 'all'>('all')
const chatExpanded = ref(false)
const chartRef = ref<HTMLElement>()
let chartInstance: echarts.ECharts | null = null

// 辅助函数：过滤掉 system 角色的消息
const filterChatHistory = (messages: ApiChatMessage[]): ChatMessage[] => {
  return messages
    .filter((msg) => msg.role === 'user' || msg.role === 'assistant')
    .map((msg) => ({
      role: msg.role as 'user' | 'assistant',
      content: msg.content,
    }))
}

// 计算属性
const hasConsultation = computed(() => {
  return !!consultationData.value && !!consultationData.value.chat_history?.length
})

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

const riskLabel = computed(() => {
  const map: Record<string, string> = {
    good: '良好',
    moderate: '中等',
    severe: '高风险',
  }
  return map[riskLevel.value] || '良好'
})

const riskPercentage = computed(() => {
  const map: Record<string, number> = {
    good: 20,
    moderate: 55,
    severe: 85,
  }
  return map[riskLevel.value] || 20
})

const topDimensions = computed(() => {
  if (!reportData.value?.charts?.radar_data) return []
  return [...reportData.value.charts.radar_data].sort((a, b) => b.value - a.value).slice(0, 5)
})

const displayedMessages = computed(() => {
  const messages = consultationData.value?.chat_history || []
  if (chatExpanded.value) return messages
  return messages.slice(0, 4) // 默认显示前4条
})

const renderedMarkdown = computed(() => {
  const md = reportData.value?.content?.advice_md
  if (!md) return ''

  marked.setOptions({ breaks: true, gfm: true })
  const html = marked.parse(md) as string
  return DOMPurify.sanitize(html)
})

// 生命周期
onMounted(async () => {
  await fetchAllData()
})

onBeforeUnmount(() => {
  if (chartInstance) {
    chartInstance.dispose()
  }
  window.removeEventListener('resize', handleResize)
})

// 监听activeSection变化，在显示测评报告时初始化图表
watch(activeSection, (newVal) => {
  if (newVal === 'assessment' || newVal === 'all') {
    nextTick(() => {
      initChart()
    })
  }
})

// 数据获取
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

    // 并行请求测评报告
    const reportRes = await getReportDetail(reportId, uid)

    if (reportRes.code === 200) {
      reportData.value = reportRes.data
    } else {
      throw new Error(reportRes.msg || '获取测评报告失败')
    }

    // 如果有consultationId，同时获取问诊详情
    if (consultationId) {
      try {
        const consultRes = await getConsultationDetail(consultationId)
        if (consultRes.code === 200) {
          const apiData = consultRes.data as ApiConsultationData

          // 转换数据格式，过滤掉 system 消息
          consultationData.value = {
            date: apiData.date,
            diagnosis_report: apiData.diagnosis_report,
            chat_history: filterChatHistory(apiData.chat_history || []),
          }
        }
      } catch (err) {
        console.warn('获取问诊详情失败，但不影响测评报告展示', err)
      }
    }

    // 初始化图表
    nextTick(() => {
      initChart()
    })
  } catch (err: unknown) {
    error.value = {
      title: '加载失败',
      message: err instanceof Error ? err.message : '获取报告数据失败，请检查网络连接',
    }
    console.error('获取报告失败:', err)
  } finally {
    loading.value = false
  }
}

// 图表初始化
const initChart = () => {
  if (!chartRef.value || !reportData.value?.charts?.radar_data) return

  if (chartInstance) {
    chartInstance.dispose()
  }

  chartInstance = echarts.init(chartRef.value)

  const chartData = reportData.value.charts.radar_data
  const indicator = chartData.map((item) => ({
    name: item.name,
    max: item.fullMark || 5,
  }))
  const values = chartData.map((item) => item.value)

  const option: echarts.EChartsOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}分',
    },
    radar: {
      indicator,
      shape: 'circle',
      splitNumber: 4,
      axisName: {
        color: '#546e7a',
        fontSize: 12,
      },
      splitLine: {
        lineStyle: { color: 'rgba(0, 137, 123, 0.1)' },
      },
      splitArea: {
        areaStyle: { color: ['rgba(0, 137, 123, 0.02)', 'rgba(0, 137, 123, 0.05)'] },
      },
      axisLine: {
        lineStyle: { color: 'rgba(0, 137, 123, 0.2)' },
      },
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

const handleResize = () => {
  chartInstance?.resize()
}

// 辅助方法
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

// 导航方法
const goHome = () => router.push('/home')
const goBack = () => router.back()
const retry = () => fetchAllData()

const startChat = () => {
  const reportId = route.params.reportId
  router.push({
    name: 'consultationChat',
    params: { reportId },
  })
}

const continueChat = () => {
  const reportId = route.params.reportId
  router.push({
    name: 'consultationChat',
    params: { reportId },
  })
}
</script>

<style scoped>
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
  -webkit-backdrop-filter: blur(20px);
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

/* ============ 问诊部分 ============ */
.consultation-section {
  margin-bottom: 35px;
}

.consultation-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

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

.diagnosis-text {
  color: #455a64;
  font-size: 15px;
  line-height: 1.9;
  white-space: pre-wrap;
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

/* 对话卡片 */
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

.legend-item {
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
  .consultation-content,
  .report-details {
    grid-template-columns: 1fr;
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
}
</style>
