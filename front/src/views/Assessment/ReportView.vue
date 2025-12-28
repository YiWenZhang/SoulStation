<!-- views/Assessment/ReportView.vue -->
<template>
  <div class="report-container">
    <!-- 背景装饰元素 -->
    <div class="background-decoration">
      <div class="bubble bubble-1"></div>
      <div class="bubble bubble-2"></div>
      <div class="bubble bubble-3"></div>
      <div class="floating-icon">📊</div>
      <div class="floating-icon">📈</div>
      <div class="floating-icon">💡</div>
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
            <span class="title-icon">📋</span>
            心理健康测评报告
            <span class="title-badge" :class="riskClass">{{ riskLabel }}</span>
          </h1>
          <p class="page-subtitle">专业分析，科学建议，助力心灵成长</p>
        </div>
        <div class="header-right">
          <div class="action-buttons">
            <button
              class="action-btn chat-btn"
              @click="startChat"
              v-if="reportData?.actions?.can_chat"
            >
              <span class="btn-icon">💬</span>
              <span class="btn-text">AI咨询</span>
            </button>
            <button
              class="action-btn download-btn"
              :class="{ downloading: downloading }"
              @click="downloadReport"
              :disabled="downloading"
              v-if="reportData?.actions?.can_download"
            >
              <span class="btn-icon" v-if="!downloading">⬇️</span>
              <span class="loading-spinner" v-else></span>
              <span class="btn-text">{{ downloading ? '生成中...' : '下载报告' }}</span>
            </button>

            <button class="action-btn back-btn" @click="goHome">
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
        <h3 class="loading-title">正在生成测评报告</h3>
        <p class="loading-subtitle">数据分析中，请稍候...</p>
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
    <main class="main-content" v-else-if="reportData" ref="reportContentRef">
      <!-- 报告概览 -->
      <div class="report-overview">
        <div class="card overview-card">
          <div class="overview-header">
            <div class="report-meta">
              <div class="report-id">
                <span class="meta-icon">📄</span>
                <span class="meta-label">报告编号</span>
                <span class="meta-value">{{ reportData.base_info.report_no || '--' }}</span>
              </div>
              <div class="report-date">
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
                <p class="risk-summary">
                  {{ reportData.core_result.summary_label || '正在分析您的心理状态...' }}
                </p>
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
            <div class="risk-tips">
              <div class="tip-item">
                <span class="tip-icon">💡</span>
                <span class="tip-text">{{
                  reportData.core_result.score_interpretation || '分数越高代表症状越明显'
                }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="report-details">
        <!-- 左侧：雷达图 -->
        <div class="report-left">
          <div class="card chart-card">
            <div class="card-header">
              <h3 class="card-title">
                <span class="title-icon">📈</span>
                心理维度雷达图
              </h3>
            </div>
            <div class="chart-container">
              <div ref="chartRef" class="chart" v-if="reportData.charts?.radar_data?.length"></div>
              <div v-else class="no-chart-data">
                <div class="no-data-icon">📊</div>
                <p class="no-data-text">暂无图表数据</p>
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
                关键指标分析（前5个）
              </h3>
            </div>
            <div class="metrics-grid">
              <div class="metric-item" v-for="item in topDimensions" :key="item.name">
                <div class="metric-header">
                  <span class="metric-name">{{ item.name }}</span>
                  <span class="metric-score" :class="getScoreClass(item.value)">{{
                    item.value.toFixed(1)
                  }}</span>
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
                  {{ getRiskLevel(item.value) }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧：详细报告 -->
        <div class="report-right">
          <div class="card report-content-card">
            <div class="card-header">
              <h3 class="card-title">
                <span class="title-icon">📝</span>
                详细分析与建议
              </h3>
              <div class="content-tabs">
                <button
                  class="tab-btn"
                  :class="{ active: activeTab === 'advice' }"
                  @click="activeTab = 'advice'"
                >
                  专业建议
                </button>
                <button
                  class="tab-btn"
                  :class="{ active: activeTab === 'summary' }"
                  @click="activeTab = 'summary'"
                >
                  核心摘要
                </button>
              </div>
            </div>

            <div class="report-content">
              <!-- Markdown 渲染区域 -->
              <div v-if="activeTab === 'advice'" class="custom-advice-list">
                <div class="advice-section-header">
                  <h3>📊 测评结果综述</h3>
                  <p class="summary-stats">
                    本次测评总分 <strong>{{ reportData.core_result.total_score || 0 }}</strong
                    >， 平均分 <strong>{{ reportData.core_result.total_avg || 0 }}</strong
                    >。
                  </p>
                  <div class="summary-quote">
                    {{
                      reportData.core_result.overall_advice || reportData.core_result.summary_label
                    }}
                  </div>
                </div>

                <hr class="advice-divider" />

                <div class="advice-section-body">
                  <h3>🧩 维度详细分析</h3>

                  <div
                    class="dimension-detail-item"
                    v-for="item in reportData.dimensions_detail"
                    :key="item.name"
                  >
                    <div class="dim-header">
                      <h4 class="dim-title">
                        {{ item.name }}
                        <span class="dim-badge" :class="getRiskTagClass(item.score)">
                          {{ item.level }}
                        </span>
                      </h4>
                      <span class="dim-score-val">指数: {{ item.score }}</span>
                    </div>

                    <p class="dim-desc"><strong>分析：</strong>{{ item.description }}</p>
                  </div>
                </div>
              </div>

              <!-- 核心摘要 -->
              <div v-else-if="activeTab === 'summary'" class="summary-content">
                <div class="summary-section">
                  <h4 class="summary-title">测评结果概览</h4>
                  <p class="summary-text">
                    本次测评基于{{ reportData.base_info.mode_name || '专业量表' }}，
                    您的综合风险等级为 <strong :class="riskClass">{{ riskTitle }}</strong
                    >。
                    {{ reportData.core_result.summary_label || '' }}
                  </p>
                </div>

                <div class="summary-section" v-if="topDimensions.length">
                  <h4 class="summary-title">重点关注维度</h4>
                  <div class="dimension-list">
                    <div
                      class="dimension-item"
                      v-for="item in topDimensions.slice(0, 3)"
                      :key="item.name"
                    >
                      <div class="dimension-info">
                        <span class="dimension-name">{{ item.name }}</span>
                        <span class="dimension-score">{{ item.value.toFixed(1) }}</span>
                      </div>
                      <div class="dimension-progress">
                        <div class="progress-bar">
                          <div
                            class="progress-fill"
                            :style="{
                              width: Math.min((item.value / 5) * 100, 100) + '%',
                              backgroundColor: getDimensionColor(item.value),
                            }"
                          ></div>
                        </div>
                        <span class="progress-label">{{ getRiskLevel(item.value) }}</span>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="summary-section">
                  <h4 class="summary-title">后续建议</h4>
                  <ul class="suggestion-list">
                    <li v-if="riskLevel === 'good'">继续保持良好的心理状态和健康生活习惯</li>
                    <li v-if="riskLevel === 'moderate'">建议关注情绪变化，适当进行压力管理</li>
                    <li v-if="riskLevel === 'severe'">建议寻求专业心理咨询师的帮助</li>
                    <li>定期进行心理测评，跟踪心理状态变化</li>
                    <li>结合AI咨询功能获取个性化建议</li>
                  </ul>
                </div>
              </div>
            </div>

            <div class="content-footer">
              <div class="disclaimer">
                <span class="disclaimer-icon">⚠️</span>
                <span class="disclaimer-text">
                  本报告仅供参考，不构成专业医疗建议。如有需要，请咨询专业心理医生。
                </span>
              </div>
              <div class="print-actions">
                <button class="print-btn" @click="printReport">
                  <span class="print-icon">🖨️</span>
                  <span class="print-text">打印报告</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Toast 提示 -->
    <Teleport to="body">
      <Transition name="toast-slide">
        <div v-if="toastVisible" class="toast-container" :class="toastType">
          <span class="toast-icon">
            {{ toastType === 'success' ? '✅' : toastType === 'error' ? '❌' : '💡' }}
          </span>
          <span class="toast-message">{{ toastMessage }}</span>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import * as echarts from 'echarts'
// import { marked } from 'marked'
// import DOMPurify from 'dompurify'
import html2canvas from 'html2canvas'
import { getReportDetail } from '../../api/assessment'

interface ErrorInfo {
  title: string
  message: string
}

interface DimensionItem {
  name: string
  value: number
  fullMark: number
}

interface DimensionDetail {
  name: string
  score: number
  level: string
  level_int: number
  description: string
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
    // === 【修改点 2】补充后端返回的总分和建议字段 ===
    total_score?: number
    total_avg?: number
    overall_advice?: string
  }
  charts: {
    radar_data: DimensionItem[]
  }
  dimensions_detail: DimensionDetail[]
  content: {
    advice_md: string
  }
  actions: {
    can_chat: boolean
    can_download: boolean
  }
}

const route = useRoute()
const router = useRouter()

// --- 状态定义 ---
const loading = ref(true)
const error = ref<ErrorInfo | null>(null)
const reportData = ref<ReportData | null>(null)
const activeTab = ref<'advice' | 'summary'>('advice')
const chartRef = ref<HTMLElement>()
const reportContentRef = ref<HTMLElement>()
const downloading = ref(false)
let chartInstance: echarts.ECharts | null = null

// --- 计算属性 ---
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
    severe: '高',
  }
  return map[riskLevel.value] || '良好'
})

const riskPercentage = computed(() => {
  const map: Record<string, number> = {
    good: 20,
    moderate: 60,
    severe: 90,
  }
  return map[riskLevel.value] || 20
})

const topDimensions = computed(() => {
  if (!reportData.value?.charts?.radar_data) return []
  return [...reportData.value.charts.radar_data]
    .sort((a: DimensionItem, b: DimensionItem) => b.value - a.value)
    .slice(0, 5)
})

// const renderedMarkdown = computed(() => {
//   const md = reportData.value?.content?.advice_md
//   if (!md) return ''

//   marked.setOptions({
//     breaks: true,
//     gfm: true,
//   })

//   const html = marked.parse(md) as string
//   return DOMPurify.sanitize(html)
// })

// --- 生命周期 ---
onMounted(() => {
  fetchReportData()
})

onBeforeUnmount(() => {
  if (chartInstance) {
    chartInstance.dispose()
  }
})

// --- 方法 ---
const fetchReportData = async () => {
  const reportId = route.params.id
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

    const response = await getReportDetail(reportId.toString(), uid)

    if (response.code === 200) {
      reportData.value = response.data
      nextTick(() => {
        initChart()
      })
    } else {
      handleError(response.code, response.msg)
    }
  } catch (err) {
    error.value = {
      title: '网络错误',
      message: '获取报告数据失败，请检查网络连接',
    }
    console.error('获取报告失败:', err)
  } finally {
    loading.value = false
  }
}

const handleError = (code: number, message: string) => {
  const errorMap: Record<number, { title: string; message: string }> = {
    400: { title: '参数错误', message: '请求参数不正确' },
    403: { title: '权限不足', message: '您无权查看此报告' },
    404: { title: '报告不存在', message: '请求的报告不存在或已被删除' },
    500: { title: '服务器错误', message: '服务器内部错误，请稍后重试' },
  }

  error.value = errorMap[code] || {
    title: '获取失败',
    message: message || '未知错误',
  }
}

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
      indicator: indicator,
      shape: 'circle',
      splitNumber: 4,
      axisName: {
        color: '#546e7a',
        fontSize: 12,
        padding: [0, 0],
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(0, 137, 123, 0.1)',
        },
      },
      splitArea: {
        areaStyle: {
          color: ['rgba(0, 137, 123, 0.02)', 'rgba(0, 137, 123, 0.05)'],
        },
      },
      axisLine: {
        lineStyle: {
          color: 'rgba(0, 137, 123, 0.2)',
        },
      },
    },
    series: [
      {
        type: 'radar',
        data: [
          {
            value: values,
            name: '心理维度',
            itemStyle: {
              color: '#00897b',
            },
            areaStyle: {
              color: {
                type: 'radial',
                x: 0.5,
                y: 0.5,
                r: 0.5,
                colorStops: [
                  {
                    offset: 0,
                    color: 'rgba(0, 137, 123, 0.3)',
                  },
                  {
                    offset: 1,
                    color: 'rgba(0, 137, 123, 0.1)',
                  },
                ],
              },
            },
            lineStyle: {
              width: 2,
              color: '#00897b',
            },
            symbol: 'circle',
            symbolSize: 8,
            label: {
              show: true,
              formatter: '{c}',
              color: '#00897b',
              fontSize: 12,
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
  if (chartInstance) {
    chartInstance.resize()
  }
}

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

const getRiskLevel = (value: number): string => {
  if (value <= 2) return '良好'
  if (value <= 3) return '中等'
  return '较高'
}

const getRiskTagClass = (value: number): string => {
  if (value <= 2) return 'tag-good'
  if (value <= 3) return 'tag-moderate'
  return 'tag-severe'
}

const startChat = () => {
  // 获取当前报告ID
  const reportId = route.params.id

  if (!reportId) {
    showToast('报告ID缺失，无法发起问诊', 'error')
    return
  }

  // 跳转到AI问诊聊天页面，带上报告ID
  router.push({
    name: 'consultationChat',
    params: { reportId },
  })
}

const downloadReport = async () => {
  if (!reportContentRef.value || downloading.value) return

  downloading.value = true

  try {
    const reportNo = reportData.value?.base_info?.report_no || 'report'
    const date = reportData.value?.base_info?.date || new Date().toISOString().split('T')[0]

    const originalStyle = reportContentRef.value.style.cssText

    const canvas = await html2canvas(reportContentRef.value, {
      scale: 2,
      useCORS: true,
      backgroundColor: '#f8f9ff',
      logging: false,
      allowTaint: true,
      windowWidth: reportContentRef.value.scrollWidth,
      windowHeight: reportContentRef.value.scrollHeight,
      onclone: (clonedDoc) => {
        const clonedElement = clonedDoc.querySelector('.main-content') as HTMLElement
        if (clonedElement) {
          clonedElement.style.padding = '40px'
          clonedElement.style.maxWidth = 'none'
        }
      },
    })

    reportContentRef.value.style.cssText = originalStyle

    canvas.toBlob(
      (blob) => {
        if (blob) {
          const url = URL.createObjectURL(blob)
          const link = document.createElement('a')
          link.href = url
          link.download = `心理测评报告_${reportNo}_${date}.png`
          document.body.appendChild(link)
          link.click()
          document.body.removeChild(link)
          URL.revokeObjectURL(url)

          showToast('报告下载成功！', 'success')
        } else {
          showToast('生成图片失败，请重试', 'error')
        }
      },
      'image/png',
      1.0,
    )
  } catch (err) {
    console.error('下载报告失败:', err)
    showToast('下载失败，请稍后重试', 'error')
  } finally {
    downloading.value = false
  }
}

// Toast 提示相关
const toastVisible = ref(false)
const toastMessage = ref('')
const toastType = ref<'success' | 'error' | 'info'>('info')
let toastTimer: ReturnType<typeof setTimeout> | null = null

const showToast = (message: string, type: 'success' | 'error' | 'info' = 'info') => {
  if (toastTimer) clearTimeout(toastTimer)

  toastMessage.value = message
  toastType.value = type
  toastVisible.value = true

  toastTimer = setTimeout(() => {
    toastVisible.value = false
  }, 3000)
}

const goHome = () => {
  router.push('/home')
}

const retry = () => {
  fetchReportData()
}

const printReport = () => {
  window.print()
}
</script>

<style scoped>
/* 复用问卷页面的基础样式 */
.report-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8f9ff 0%, #f0f7ff 100%);
  position: relative;
}

/* === 优化后的维度列表样式 === */

.custom-advice-list {
  padding: 10px 0;
}

/* 综述头部 */
.advice-section-header {
  background: linear-gradient(135deg, rgba(0, 137, 123, 0.03), rgba(0, 137, 123, 0.08));
  padding: 20px;
  border-radius: 16px;
  margin-bottom: 25px;
}

.advice-section-header h3 {
  color: #00897b;
  font-size: 18px;
  margin-bottom: 12px;
  font-weight: 800;
  display: flex;
  align-items: center;
  gap: 8px;
}

.summary-stats {
  font-size: 15px;
  color: #546e7a;
  margin-bottom: 12px;
}

.summary-stats strong {
  color: #263238;
  font-size: 18px;
  font-family: 'DIN Alternate', 'Roboto', sans-serif; /* 数字字体 */
}

.summary-quote {
  background: #ffffff;
  border-left: 4px solid #00897b;
  padding: 12px 16px;
  color: #455a64;
  border-radius: 0 8px 8px 0;
  font-size: 14px;
  line-height: 1.6;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
}

.advice-divider {
  border: 0;
  height: 1px;
  background: linear-gradient(
    to right,
    rgba(0, 137, 123, 0),
    rgba(0, 137, 123, 0.2),
    rgba(0, 137, 123, 0)
  );
  margin: 30px 0;
}

/* 维度详细列表容器 */
.advice-section-body h3 {
  color: #263238;
  font-size: 18px;
  margin-bottom: 20px;
  padding-left: 10px;
  border-left: 4px solid #00897b;
  font-weight: 700;
}

/* === 核心：维度卡片美化 === */
.dimension-detail-item {
  background: #ffffff;
  border-radius: 16px;
  padding: 20px 24px;
  margin-bottom: 18px;
  /* 阴影更柔和 */
  box-shadow:
    0 4px 6px rgba(0, 0, 0, 0.02),
    0 10px 15px rgba(0, 0, 0, 0.03);
  border: 1px solid rgba(0, 0, 0, 0.03);
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  position: relative;
  overflow: hidden;
}

/* 鼠标悬停效果 */
.dimension-detail-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 25px rgba(0, 137, 123, 0.12);
  border-color: rgba(0, 137, 123, 0.15);
}

/* 卡片顶部布局：标题左，分数右 */
.dim-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.dim-title-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.dim-title {
  margin: 0;
  font-size: 17px;
  font-weight: 700;
  color: #37474f;
}

/* 徽标样式优化 */
.dim-badge {
  font-size: 11px;
  padding: 3px 10px;
  border-radius: 20px;
  color: white;
  letter-spacing: 0.5px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* 不同等级的颜色定义 (复用你的逻辑) */
.dim-badge.tag-good {
  background: linear-gradient(135deg, #66bb6a, #43a047);
}
.dim-badge.tag-moderate {
  background: linear-gradient(135deg, #ffa726, #fb8c00);
}
.dim-badge.tag-severe {
  background: linear-gradient(135deg, #ef5350, #e53935);
}

/* 右侧大分数 */
.dim-score-box {
  text-align: right;
}
.dim-score-val {
  font-family: 'DIN Alternate', 'Roboto', sans-serif;
  font-weight: 700;
  font-size: 24px;
  line-height: 1;
  color: #00897b;
}
.dim-score-label {
  font-size: 10px;
  color: #90a4ae;
  display: block;
  margin-top: 2px;
}

/* 分数颜色变化 */
.score-color-good {
  color: #43a047;
}
.score-color-mod {
  color: #fb8c00;
}
.score-color-sev {
  color: #e53935;
}

/* 描述文本 */
.dim-desc {
  margin: 15px 0 0 0;
  color: #546e7a;
  font-size: 14px;
  line-height: 1.7;
  background: #fcfcfc; /* 极淡的背景区分 */
  padding: 12px;
  border-radius: 8px;
  border: 1px dashed rgba(0, 0, 0, 0.05);
}

.dim-desc strong {
  color: #263238;
  font-weight: 600;
}

/* === 新增：进度条装饰 === */
/* 你需要在 HTML 模板里也加上这个 div 结构，如果不加，CSS 不会生效但也不会报错 */
.dim-progress-bg {
  height: 6px;
  background: #f0f2f5;
  border-radius: 3px;
  margin-top: 10px;
  overflow: hidden;
  width: 100%;
}
.dim-progress-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 1s ease-out;
}

/* 背景装饰 */
.background-decoration {
  position: fixed;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

.bubble {
  position: absolute;
  border-radius: 50%;
  background: rgba(0, 137, 123, 0.05);
  animation: float 20s infinite ease-in-out;
}

.bubble-1 {
  width: 300px;
  height: 300px;
  top: -150px;
  right: -100px;
}
.bubble-2 {
  width: 200px;
  height: 200px;
  bottom: 100px;
  left: -50px;
  animation-delay: -5s;
}
.bubble-3 {
  width: 150px;
  height: 150px;
  top: 30%;
  right: 20%;
  animation-delay: -10s;
}

.floating-icon {
  position: absolute;
  font-size: 24px;
  opacity: 0.1;
  animation: float 15s infinite ease-in-out;
}

@keyframes float {
  0%,
  100% {
    transform: translateY(0) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(10deg);
  }
}

/* 页面头部 */
.page-header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(0, 137, 123, 0.1);
  padding: 15px 30px;
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
  transition: transform 0.3s ease;
}

.logo-section:hover {
  transform: scale(1.05);
}

.logo-icon {
  font-size: 32px;
  animation: gentlePulse 4s infinite ease-in-out;
}

@keyframes gentlePulse {
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
  margin: 2px 0 0 0;
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
  gap: 10px;
  font-weight: 700;
}

.title-icon {
  font-size: 24px;
}

.title-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  background: linear-gradient(135deg, #00897b, #00acc1);
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
  margin: 6px 0 0 0;
}

.header-right .action-buttons {
  display: flex;
  gap: 10px;
}

.action-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}

.chat-btn {
  background: linear-gradient(135deg, #00897b, #00acc1);
  color: white;
}

.download-btn {
  background: linear-gradient(135deg, #4caf50, #66bb6a);
  color: white;
}

.back-btn {
  background: rgba(0, 137, 123, 0.1);
  color: #00897b;
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* 主内容区域 */
.main-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 30px 20px;
  position: relative;
  z-index: 1;
}

/* 报告概览 */
.report-overview {
  margin-bottom: 25px;
}

.overview-card {
  background: white;
  border-radius: 20px;
  padding: 25px;
  box-shadow: 0 8px 30px rgba(0, 137, 123, 0.1);
}

.overview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid rgba(0, 137, 123, 0.1);
}

.report-meta {
  display: flex;
  gap: 30px;
}

.report-id,
.report-date {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #546e7a;
  font-size: 13px;
}

.meta-icon {
  font-size: 16px;
}

.meta-label {
  color: #90a4ae;
}

.meta-value {
  color: #263238;
  font-weight: 600;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.avatar {
  width: 50px;
  height: 50px;
  background: linear-gradient(135deg, #00897b, #00acc1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.user-details {
  display: flex;
  flex-direction: column;
}

.user-name {
  color: #263238;
  font-size: 18px;
  margin: 0 0 4px 0;
  font-weight: 700;
}

.assessment-name {
  color: #90a4ae;
  font-size: 12px;
  margin: 0;
}

/* 风险卡片 */
.risk-card {
  border-radius: 15px;
  padding: 20px;
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
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
  gap: 20px;
  margin-bottom: 15px;
}

.risk-icon {
  font-size: 48px;
  width: 80px;
  height: 80px;
  background: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.risk-details {
  flex: 1;
}

.risk-title {
  font-size: 24px;
  margin: 0 0 10px 0;
  color: #263238;
  font-weight: 700;
}

.risk-summary {
  color: #546e7a;
  font-size: 14px;
  margin: 0 0 15px 0;
  line-height: 1.5;
}

.risk-indicator {
  background: rgba(255, 255, 255, 0.8);
  border-radius: 10px;
  padding: 15px;
}

.indicator-bar {
  height: 8px;
  background: linear-gradient(to right, #4caf50, #ff9800, #f44336);
  border-radius: 4px;
  position: relative;
  margin-bottom: 8px;
}

.indicator-fill {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 4px;
  transition: width 1s ease;
}
/* 添加下面的样式 */
.indicator-marker {
  position: absolute;
  top: 50%;
  width: 18px;
  height: 18px;
  background: white;
  border: 3px solid #263238;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  transition: left 1s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25);
  z-index: 1;
}
.indicator-labels {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: #90a4ae;
  font-weight: 600;
}

.risk-tips {
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 10px;
  border-left: 4px solid #00897b;
}

.tip-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.tip-icon {
  font-size: 16px;
  color: #00897b;
}

.tip-text {
  color: #546e7a;
  font-size: 13px;
  line-height: 1.4;
}

/* 报告详情布局 */
.report-details {
  display: flex;
  gap: 25px;
  margin-bottom: 25px;
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

/* 卡片样式 */
.card {
  background: white;
  border-radius: 20px;
  box-shadow: 0 8px 30px rgba(0, 137, 123, 0.1);
  border: 1px solid rgba(0, 137, 123, 0.05);
}

.chart-card,
.metrics-card,
.report-content-card {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid rgba(0, 137, 123, 0.1);
}

.card-title {
  color: #263238;
  font-size: 18px;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 700;
}

.title-icon {
  font-size: 20px;
}

/* 图表容器 */
.chart-container {
  height: 300px;
  width: 100%;
  position: relative;
}

.chart {
  width: 100%;
  height: 100%;
}

.no-chart-data {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #90a4ae;
}

.no-data-icon {
  font-size: 48px;
  margin-bottom: 15px;
  opacity: 0.3;
}

.no-data-text {
  font-size: 14px;
  margin: 0;
}

.chart-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid rgba(0, 137, 123, 0.1);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: rgba(0, 137, 123, 0.05);
  border-radius: 20px;
  font-size: 12px;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.legend-name {
  color: #263238;
  font-weight: 600;
}

.legend-value {
  color: #00897b;
  font-weight: 700;
  font-size: 13px;
}

/* 指标网格 */
.metrics-grid {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.metric-item {
  background: rgba(0, 137, 123, 0.03);
  border: 1px solid rgba(0, 137, 123, 0.1);
  border-radius: 12px;
  padding: 15px;
  transition: all 0.3s ease;
}

.metric-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0, 137, 123, 0.1);
}

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.metric-name {
  color: #263238;
  font-size: 14px;
  font-weight: 600;
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
  transition: width 1s ease;
}

.metric-tag {
  display: inline-block;
  padding: 4px 10px;
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

/* 内容标签页 */
.content-tabs {
  display: flex;
  gap: 5px;
  background: rgba(0, 137, 123, 0.05);
  padding: 4px;
  border-radius: 12px;
}

.tab-btn {
  padding: 8px 20px;
  border: none;
  background: transparent;
  color: #546e7a;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.tab-btn.active {
  background: white;
  color: #00897b;
  box-shadow: 0 2px 8px rgba(0, 137, 123, 0.1);
}

/* Markdown 内容样式 */
.markdown-content {
  color: #37474f;
  line-height: 1.8;
  font-size: 15px;
}

.markdown-content :deep(h1) {
  color: #00897b;
  font-size: 24px;
  margin: 30px 0 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid rgba(0, 137, 123, 0.1);
}

.markdown-content :deep(h2) {
  color: #263238;
  font-size: 20px;
  margin: 25px 0 15px;
  font-weight: 700;
}

.markdown-content :deep(h3) {
  color: #00897b;
  font-size: 18px;
  margin: 20px 0 15px;
  padding-left: 15px;
  border-left: 4px solid #00897b;
  font-weight: 700;
}

.markdown-content :deep(h4) {
  color: #546e7a;
  font-size: 16px;
  margin: 15px 0 10px;
  font-weight: 600;
}

.markdown-content :deep(p) {
  margin: 15px 0;
  color: #455a64;
}

.markdown-content :deep(strong) {
  color: #00897b;
  font-weight: 700;
}

.markdown-content :deep(em) {
  color: #ff9800;
  font-style: italic;
}

.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  margin: 15px 0;
  padding-left: 25px;
}

.markdown-content :deep(li) {
  margin: 8px 0;
  color: #455a64;
}

.markdown-content :deep(blockquote) {
  border-left: 4px solid #00897b;
  padding: 15px 20px;
  margin: 20px 0;
  background: rgba(0, 137, 123, 0.05);
  border-radius: 0 8px 8px 0;
  font-style: italic;
}

.markdown-content :deep(code) {
  background: rgba(0, 137, 123, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  color: #00897b;
}

.markdown-content :deep(pre) {
  background: #263238;
  color: #e0e0e0;
  padding: 20px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 20px 0;
}

.markdown-content :deep(pre code) {
  background: transparent;
  color: inherit;
  padding: 0;
}

.markdown-content :deep(a) {
  color: #00897b;
  text-decoration: none;
  border-bottom: 1px solid rgba(0, 137, 123, 0.3);
  transition: all 0.3s ease;
}

.markdown-content :deep(a:hover) {
  color: #00acc1;
  border-bottom-color: #00acc1;
}

.markdown-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 20px 0;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.markdown-content :deep(th) {
  background: #00897b;
  color: white;
  font-weight: 600;
  text-align: left;
  padding: 12px 15px;
}

.markdown-content :deep(td) {
  padding: 12px 15px;
  border-bottom: 1px solid rgba(0, 137, 123, 0.1);
  color: #455a64;
}

.markdown-content :deep(tr:hover) {
  background: rgba(0, 137, 123, 0.03);
}

/* 摘要内容 */
.summary-content {
  padding: 20px;
}

.summary-section {
  margin-bottom: 25px;
}

.summary-title {
  color: #00897b;
  font-size: 16px;
  margin: 0 0 15px 0;
  padding-bottom: 8px;
  border-bottom: 2px solid rgba(0, 137, 123, 0.1);
  font-weight: 700;
}

.summary-text {
  color: #546e7a;
  line-height: 1.6;
  margin: 0 0 15px 0;
}

.dimension-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.dimension-item {
  background: rgba(0, 137, 123, 0.03);
  border: 1px solid rgba(0, 137, 123, 0.1);
  border-radius: 10px;
  padding: 15px;
}

.dimension-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.dimension-name {
  color: #263238;
  font-weight: 600;
  font-size: 14px;
}

.dimension-score {
  font-size: 18px;
  font-weight: 700;
  color: #00897b;
}

.dimension-progress {
  display: flex;
  align-items: center;
  gap: 15px;
}

.progress-bar {
  flex: 1;
  height: 6px;
  background: rgba(0, 137, 123, 0.1);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 1s ease;
}

.progress-label {
  font-size: 12px;
  font-weight: 600;
  color: #00897b;
  min-width: 60px;
}

.suggestion-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.suggestion-list li {
  padding: 10px 0 10px 25px;
  position: relative;
  color: #546e7a;
  line-height: 1.6;
}

.suggestion-list li::before {
  content: '•';
  color: #00897b;
  font-size: 20px;
  position: absolute;
  left: 0;
  top: 8px;
}

/* 内容页脚 */
.content-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 20px;
  margin-top: 20px;
  border-top: 1px solid rgba(0, 137, 123, 0.1);
}

.disclaimer {
  display: flex;
  align-items: center;
  gap: 10px;
  max-width: 70%;
}

.disclaimer-icon {
  font-size: 16px;
  color: #ff9800;
  flex-shrink: 0;
}

.disclaimer-text {
  color: #90a4ae;
  font-size: 12px;
  line-height: 1.4;
}

.print-actions {
  display: flex;
  gap: 10px;
}

.print-btn {
  padding: 8px 16px;
  border: 1px solid rgba(0, 137, 123, 0.2);
  background: white;
  border-radius: 8px;
  color: #00897b;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s ease;
}

.print-btn:hover {
  background: rgba(0, 137, 123, 0.1);
  transform: translateY(-2px);
}

/* 加载和错误状态 */
.loading-state,
.error-state {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
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
  padding: 40px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 137, 123, 0.2);
}

.loading-animation {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-bottom: 30px;
}

.loading-circle {
  width: 20px;
  height: 20px;
  background: linear-gradient(135deg, #00897b, #00acc1);
  border-radius: 50%;
  animation: loadingBounce 1.4s infinite ease-in-out;
}

@keyframes loadingBounce {
  0%,
  80%,
  100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

.loading-title {
  color: #263238;
  font-size: 22px;
  margin: 0 0 10px 0;
}

.loading-subtitle {
  color: #90a4ae;
  margin: 0;
}

.error-icon {
  font-size: 64px;
  margin-bottom: 20px;
  color: #f44336;
}

.error-title {
  color: #263238;
  font-size: 24px;
  margin: 0 0 10px 0;
}

.error-message {
  color: #546e7a;
  margin: 0 0 30px 0;
  line-height: 1.5;
}

.error-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
}

.error-btn {
  padding: 12px 25px;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.error-btn.primary {
  background: linear-gradient(135deg, #00897b, #00acc1);
  color: white;
}

.error-btn.secondary {
  background: rgba(0, 137, 123, 0.1);
  color: #00897b;
}

.error-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .report-details {
    flex-direction: column;
  }

  .report-left,
  .report-right {
    width: 100%;
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
    gap: 15px;
  }

  .content-footer {
    flex-direction: column;
    gap: 20px;
    align-items: flex-start;
  }

  .print-actions {
    width: 100%;
    justify-content: flex-start;
  }
}

@media (max-width: 480px) {
  .page-header {
    padding: 15px;
  }

  .main-content {
    padding: 20px 15px;
  }

  .card-header {
    flex-direction: column;
    gap: 15px;
    align-items: flex-start;
  }

  .content-tabs {
    width: 100%;
  }

  .tab-btn {
    flex: 1;
    text-align: center;
  }

  .chart-container {
    height: 250px;
  }
}

/* 下载按钮加载状态 */
.download-btn.downloading {
  opacity: 0.8;
  cursor: wait;
}

.download-btn .loading-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  display: inline-block;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Toast 样式 */
.toast-container {
  position: fixed;
  top: 80px;
  left: 50%;
  transform: translateX(-50%);
  padding: 14px 28px;
  border-radius: 30px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  font-weight: 600;
  z-index: 3000;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.toast-container.success {
  background: linear-gradient(135deg, #4caf50, #66bb6a);
  color: white;
}

.toast-container.error {
  background: linear-gradient(135deg, #f44336, #ef5350);
  color: white;
}

.toast-container.info {
  background: linear-gradient(135deg, #2196f3, #42a5f5);
  color: white;
}

.toast-icon {
  font-size: 18px;
}

/* Toast 过渡动画 */
.toast-slide-enter-active,
.toast-slide-leave-active {
  transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.toast-slide-enter-from {
  opacity: 0;
  transform: translateX(-50%) translateY(-30px);
}

.toast-slide-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-30px);
}

/* 打印时隐藏某些元素 */
@media print {
  .page-header,
  .content-footer,
  .background-decoration {
    display: none !important;
  }

  .main-content {
    padding: 0 !important;
  }

  .card {
    box-shadow: none !important;
    border: 1px solid #e0e0e0 !important;
  }
}
</style>
