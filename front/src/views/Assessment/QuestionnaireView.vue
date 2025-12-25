<!-- views/Assessment/QuestionnaireView.vue -->
<template>
  <div class="assessment-container">
    <!-- 背景装饰元素 -->
    <div class="background-decoration">
      <div class="bubble bubble-1"></div>
      <div class="bubble bubble-2"></div>
      <div class="bubble bubble-3"></div>
      <div class="floating-icon">🧠</div>
      <div class="floating-icon">📝</div>
      <div class="floating-icon">⭐</div>
    </div>

    <!-- 顶部进度条 -->
    <div class="top-progress-bar">
      <div class="progress-fill" :style="{ width: progressPercentage + '%' }"></div>
      <div class="progress-info">
        <span class="progress-text">完成度</span>
        <span class="progress-percent">{{ Math.round(progressPercentage) }}%</span>
      </div>
    </div>

    <header class="page-header">
      <div class="header-content">
        <div class="header-left">
          <div class="logo-section" @click="handleGoHome">
            <div class="logo-icon">🌸</div>
            <div class="logo-text">
              <h1 class="site-title">心灵驿站</h1>
              <p class="site-subtitle">Mental Harbor</p>
              <p class="home-hint">
                <span class="hint-arrow">←</span>
                点击以返回主页
              </p>
            </div>
          </div>
        </div>
        <div class="header-center">
          <h1 class="page-title">
            <span class="title-icon">📊</span>
            心理健康专业量表测评
            <span class="title-badge">SCL-90</span>
          </h1>
          <p class="page-subtitle">科学评估您的心理状态，助力心理健康成长</p>
        </div>
        <div class="header-right">
          <div class="session-info">
            <div class="session-badge">
              <span class="badge-icon">🆔</span>
              <span class="badge-text">ID: {{ sessionId || '--' }}</span>
            </div>
            <div class="timer" v-if="!loading">
              <span class="timer-icon">⏱️</span>
              <span class="timer-text">{{ formattedTime }}</span>
            </div>
          </div>
        </div>
      </div>
    </header>

    <main class="main-content" v-if="!loading && questions.length > 0">
      <div class="question-area">
        <!-- 题目卡片 -->
        <div class="card question-card">
          <div class="card-decoration">
            <div class="wave wave-1"></div>
            <div class="wave wave-2"></div>
          </div>

          <div class="question-header">
            <div class="question-meta">
              <div class="question-number-wrapper">
                <div class="question-number">
                  <span class="number-icon">🔢</span>
                  <span class="current-num">{{ currentIndex + 1 }}</span>
                  <span class="total-num">/ {{ questions.length }}</span>
                </div>
                <div class="progress-indicator">
                  <div class="progress-dot active"></div>
                  <div
                    v-for="i in 5"
                    :key="i"
                    class="progress-dot"
                    :class="{ active: i <= (currentIndex % 5) + 1 }"
                  ></div>
                </div>
              </div>
            </div>

            <div class="question-body">
              <h2 class="question-stem">
                <span class="stem-text">{{ getCurrentQuestion()?.stem }}</span>
              </h2>

              <div class="question-tips">
                <div class="tip-item">
                  <span class="tip-icon">💡</span>
                  <span class="tip-text">请根据您最近一周的真实感受选择</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 选项列表 -->
          <div class="options-list">
            <div
              v-for="(option, idx) in getCurrentQuestion()?.options || []"
              :key="option.id"
              class="option-item"
              :class="{
                active: isOptionSelected(option.score),
                selected: isOptionSelected(option.score),
                pulse: pulseOptionId === option.id,
              }"
              @click="handleSelectOption(getCurrentQuestion()?.id || 0, option.score, option.id)"
              @mouseenter="hoverOptionIdx = idx"
              @mouseleave="hoverOptionIdx = -1"
            >
              <div class="option-content">
                <div class="option-left">
                  <div class="option-circle">
                    <div class="circle-inner">
                      <div v-if="isOptionSelected(option.score)" class="circle-dot"></div>
                    </div>
                    <div class="option-label">
                      <span class="label-text">{{ option.label }}</span>
                      <span class="label-score">({{ option.score }}分)</span>
                    </div>
                  </div>
                </div>
                <div class="option-right">
                  <div class="score-badge" v-if="hoverOptionIdx === idx">
                    <span class="score-value">{{ option.score }}分</span>
                  </div>
                  <div v-if="isOptionSelected(option.score)" class="selected-indicator">
                    <span class="indicator-icon">✓</span>
                  </div>
                </div>
              </div>

              <div v-if="isOptionSelected(option.score)" class="option-decoration">
                <div class="sparkle"></div>
                <div class="sparkle"></div>
              </div>
            </div>
          </div>

          <!-- 导航按钮 -->
          <div class="navigation-btns">
            <button
              class="nav-btn prev-btn"
              :class="{ disabled: currentIndex === 0 }"
              @click="changeQuestion(-1)"
              @mouseenter="prevBtnHover = true"
              @mouseleave="prevBtnHover = false"
            >
              <div class="btn-content">
                <span class="btn-icon">←</span>
                <span class="btn-text">上一题</span>
              </div>
              <div class="btn-wave" v-if="prevBtnHover"></div>
            </button>

            <div class="page-controls">
              <button
                v-for="page in pageNumbers"
                :key="page"
                class="page-btn"
                :class="{
                  active: currentIndex >= (page - 1) * 10 && currentIndex < page * 10,
                  answered: getPageAnsweredStatus(page),
                }"
                @click="goToPage(page)"
              >
                {{ page }}
              </button>
            </div>

            <button
              v-if="currentIndex < questions.length - 1"
              class="nav-btn next-btn"
              :class="{ disabled: !hasCurrentQuestionAnswered() }"
              @click="changeQuestion(1)"
              @mouseenter="nextBtnHover = true"
              @mouseleave="nextBtnHover = false"
            >
              <div class="btn-content">
                <span class="btn-text">下一题</span>
                <span class="btn-icon">→</span>
              </div>
              <div class="btn-wave" v-if="nextBtnHover"></div>
            </button>

            <button
              v-else
              class="nav-btn submit-btn"
              :class="{ disabled: submitting }"
              @click="handleSubmit"
              @mouseenter="submitBtnHover = true"
              @mouseleave="submitBtnHover = false"
            >
              <div class="btn-content">
                <span class="btn-icon">📤</span>
                <span class="btn-text">{{ submitting ? '提交中...' : '提交测评' }}</span>
              </div>
              <div class="btn-wave" v-if="submitBtnHover"></div>
              <div class="submit-ring" v-if="submitting"></div>
            </button>
          </div>
        </div>
      </div>

      <aside class="sidebar">
        <!-- 快速统计 -->
        <div class="card stats-card">
          <div class="stats-header">
            <div class="stats-icon">📈</div>
            <h3 class="stats-title">测评统计</h3>
          </div>
          <div class="stats-grid">
            <div class="stat-item total">
              <div class="stat-value">{{ questions.length }}</div>
              <div class="stat-label">总题数</div>
            </div>
            <div class="stat-item answered">
              <div class="stat-value">{{ answeredCount }}</div>
              <div class="stat-label">已答</div>
            </div>
            <div class="stat-item remaining">
              <div class="stat-value">{{ questions.length - answeredCount }}</div>
              <div class="stat-label">未答</div>
            </div>
            <div class="stat-item accuracy">
              <div class="stat-value">{{ answeredCount }}</div>
              <div class="stat-label">完成率</div>
            </div>
          </div>
          <div class="stats-progress">
            <div class="progress-bar-mini">
              <div class="progress-fill-mini" :style="{ width: progressPercentage + '%' }"></div>
            </div>
          </div>
        </div>

        <!-- 答题卡 -->
        <div class="card answer-sheet-card">
          <div class="sheet-header">
            <div class="sheet-icon">📋</div>
            <h3 class="sheet-title">答题卡</h3>
            <div class="sheet-tools">
              <button class="tool-btn" @click="scrollToUnanswered" title="跳转到未答题">
                <span class="tool-icon">🔍</span>
              </button>
            </div>
          </div>

          <div class="sheet-container">
            <div class="sheet-grid">
              <button
                v-for="(q, index) in questions"
                :key="q.id"
                class="grid-item"
                :class="{
                  answered: answers[q.id] !== undefined,
                  current: currentIndex === index,
                  flagged: flaggedQuestions.includes(index),
                }"
                @click="jumpToQuestion(index)"
                @contextmenu.prevent="toggleFlagQuestion(index)"
              >
                <span class="item-number">{{ index + 1 }}</span>
                <div
                  v-if="answers[q.id] !== undefined"
                  class="item-score"
                  :class="getScoreClass(answers[q.id] || 0)"
                >
                  {{ answers[q.id] }}
                </div>
                <div v-if="flaggedQuestions.includes(index)" class="item-flag">🚩</div>
              </button>
            </div>
          </div>

          <!-- 修改：删除了清空答案按钮 -->
          <div class="sheet-footer">
            <div class="sheet-legend">
              <div class="legend-item">
                <span class="legend-dot current"></span>
                <span class="legend-text">当前题</span>
              </div>
              <div class="legend-item">
                <span class="legend-dot answered"></span>
                <span class="legend-text">已答题</span>
              </div>
              <div class="legend-item">
                <span class="legend-dot flagged"></span>
                <span class="legend-text">标记题</span>
              </div>
            </div>
          </div>
        </div>
      </aside>
    </main>

    <!-- 加载状态 -->
    <div v-else-if="loading" class="loading-state">
      <div class="loading-content">
        <div class="loading-animation">
          <div class="loading-circle"></div>
          <div class="loading-circle"></div>
          <div class="loading-circle"></div>
        </div>
        <h3 class="loading-title">正在加载测评题目</h3>
        <p class="loading-subtitle">请稍候，我们正在为您准备测评...</p>
        <div class="loading-progress">
          <div class="loading-bar"></div>
        </div>
      </div>
    </div>

    <!-- 时间提示 -->
    <div v-if="!loading && questions.length > 0 && elapsedTime > 600" class="time-hint">
      <div class="hint-content">
        <span class="hint-icon">⏰</span>
        <span class="hint-text"
          >您已经认真思考了 {{ Math.floor(elapsedTime / 60) }} 分钟，请继续加油！</span
        >
      </div>
    </div>

    <!-- 无题目提示 -->
    <div v-if="!loading && questions.length === 0" class="no-questions">
      <div class="no-questions-content">
        <div class="no-questions-icon">📝</div>
        <h3 class="no-questions-title">暂无测评题目</h3>
        <p class="no-questions-subtitle">无法加载测评题目，请稍后再试或联系管理员</p>
        <button class="no-questions-btn" @click="goHome">返回首页</button>
      </div>
    </div>

    <!-- ========== 进入提示对话框========== -->
    <Teleport to="body">
      <Transition name="dialog-fade">
        <div v-if="showResumeDialog" class="dialog-overlay">
          <div class="dialog-container resume-dialog">
            <div class="dialog-header">
              <div class="dialog-icon-wrapper info">
                <span class="dialog-icon">📂</span>
              </div>
              <h3 class="dialog-title">发现未完成的测评</h3>
            </div>
            <div class="dialog-body">
              <p class="dialog-message">
                系统检测到您上次有一份未完成的测评存档（完成度
                {{
                  Math.round(
                    ((tempSessionData?.current_progress_index || 0) / (questions.length || 1)) *
                      100,
                  )
                }}%）。
              </p>
              <p class="dialog-sub-message">
                您希望继续上次的进度，还是重新开始？<br />
                <span class="note">注意：重新开始将删除旧的存档。</span>
              </p>
            </div>
            <div class="dialog-footer">
              <button class="dialog-btn secondary" @click="handleStartNewSession">
                <span class="btn-icon">🔄</span>
                <span>重新开始</span>
              </button>
              <button class="dialog-btn primary" @click="handleResumeSession">
                <span class="btn-icon">➡️</span>
                <span>继续测评</span>
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- ========== 确认提交对话框 ========== -->
    <Teleport to="body">
      <Transition name="dialog-fade">
        <div v-if="showConfirmDialog" class="dialog-overlay" @click.self="cancelSubmit">
          <div class="dialog-container confirm-dialog">
            <div class="dialog-header">
              <div class="dialog-icon-wrapper confirm">
                <span class="dialog-icon">📋</span>
              </div>
              <h3 class="dialog-title">确认提交</h3>
            </div>
            <div class="dialog-body">
              <p class="dialog-message">是否确认提交本次测评？</p>
              <div v-if="unansweredInfo.count > 0" class="warning-info">
                <span class="warning-icon">⚠️</span>
                <span class="warning-text">还有 {{ unansweredInfo.count }} 道题目未完成</span>
              </div>
            </div>
            <div class="dialog-footer">
              <button class="dialog-btn cancel" @click="cancelSubmit">
                <span class="btn-icon">👀</span>
                <span>我再看看</span>
              </button>
              <button class="dialog-btn confirm" @click="confirmSubmit" :disabled="submitting">
                <span v-if="submitting" class="loading-spinner"></span>
                <span class="btn-icon" v-else>✅</span>
                <span>{{ submitting ? '提交中...' : '确定' }}</span>
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- ========== 提交成功对话框 ========== -->
    <Teleport to="body">
      <Transition name="dialog-fade">
        <div v-if="showSuccessDialog" class="dialog-overlay">
          <div class="dialog-container success-dialog">
            <div class="dialog-header">
              <div class="dialog-icon-wrapper success">
                <span class="dialog-icon">🎉</span>
              </div>
              <h3 class="dialog-title">提交成功</h3>
            </div>
            <div class="dialog-body">
              <p class="dialog-message">您的测评已成功提交！</p>
              <div class="risk-level-badge" :class="submitResult.risk_level">
                <span class="risk-icon">{{ getRiskIcon(submitResult.risk_level) }}</span>
                <span class="risk-text">{{ getRiskLevelText(submitResult.risk_level) }}</span>
              </div>
            </div>
            <div class="dialog-footer">
              <button class="dialog-btn primary" @click="viewReport">
                <span class="btn-icon">📊</span>
                <span>查看报告</span>
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- ========== 错误提示对话框 ========== -->
    <Teleport to="body">
      <Transition name="dialog-fade">
        <div v-if="showErrorDialog" class="dialog-overlay" @click.self="closeErrorDialog">
          <div class="dialog-container error-dialog">
            <div class="dialog-header">
              <div class="dialog-icon-wrapper error">
                <span class="dialog-icon">❌</span>
              </div>
              <h3 class="dialog-title">提交失败</h3>
            </div>
            <div class="dialog-body">
              <p class="dialog-message">{{ errorMessage }}</p>
              <div v-if="errorDetails" class="error-details">
                <span class="details-text">{{ errorDetails }}</span>
              </div>
            </div>
            <div class="dialog-footer">
              <button class="dialog-btn secondary" @click="closeErrorDialog">
                <span class="btn-icon">🔙</span>
                <span>返回修改</span>
              </button>
              <button v-if="canRetry" class="dialog-btn primary" @click="retrySubmit">
                <span class="btn-icon">🔄</span>
                <span>重新提交</span>
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- ========== 新增：返回首页确认对话框 ========== -->
    <Teleport to="body">
      <Transition name="dialog-fade">
        <div v-if="showGoHomeDialog" class="dialog-overlay" @click.self="cancelGoHome">
          <div class="dialog-container go-home-dialog">
            <div class="dialog-header">
              <div class="dialog-icon-wrapper home">
                <span class="dialog-icon">🏠</span>
              </div>
              <h3 class="dialog-title">返回首页</h3>
            </div>
            <div class="dialog-body">
              <p class="dialog-message">确定要返回首页吗？</p>
              <div class="save-info">
                <span class="save-icon">💾</span>
                <span class="save-text">您的答题进度已自动保存，下次可继续作答</span>
              </div>
              <div class="progress-summary">
                <div class="summary-item">
                  <span class="summary-label">当前进度</span>
                  <span class="summary-value">{{ answeredCount }} / {{ questions.length }} 题</span>
                </div>
                <div class="summary-item">
                  <span class="summary-label">完成度</span>
                  <span class="summary-value highlight">{{ Math.round(progressPercentage) }}%</span>
                </div>
              </div>
            </div>
            <div class="dialog-footer">
              <button class="dialog-btn secondary" @click="cancelGoHome">
                <span class="btn-icon">📝</span>
                <span>继续答题</span>
              </button>
              <button class="dialog-btn primary" @click="confirmGoHome" :disabled="savingProgress">
                <span v-if="savingProgress" class="loading-spinner"></span>
                <span class="btn-icon" v-else>🏠</span>
                <span>{{ savingProgress ? '保存中...' : '返回首页' }}</span>
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- ========== Toast 提示 ========== -->
    <Teleport to="body">
      <Transition name="toast-slide">
        <div v-if="toastVisible" class="toast-container" :class="toastType">
          <span class="toast-icon">{{ toastIcon }}</span>
          <span class="toast-message">{{ toastMessage }}</span>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import {
  startAssessment,
  fetchQuestions,
  saveProgress,
  submitAssessment,
  type Question,
  type StartResponse,
} from '../../api/assessment'

// --- [新增] 状态变量 ---
const showResumeDialog = ref(false) // 控制"检测到存档"弹窗
const tempSessionData = ref<StartResponse | null>(null) // 暂存后端返回的存档数据

// 定义错误数据的类型
interface SubmitErrorData {
  total?: number
  answered?: number
  risk_level?: string
  msg?: string
  [key: string]: unknown
}

const router = useRouter()
const uid = parseInt(localStorage.getItem('uid') || '0')

// --- 状态 ---
const loading = ref(true)
const submitting = ref(false)
const sessionId = ref(0)
const questions = ref<Question[]>([])
const currentIndex = ref(0)
const answers = ref<Record<string, number>>({})
const elapsedTime = ref(0)
let timer: ReturnType<typeof setInterval> | null = null

// 新增状态
const pulseOptionId = ref<number | null>(null)
const hoverOptionIdx = ref(-1)
const prevBtnHover = ref(false)
const nextBtnHover = ref(false)
const submitBtnHover = ref(false)
const flaggedQuestions = ref<number[]>([])
const saveTimeout = ref<ReturnType<typeof setTimeout> | null>(null)

// ========== 对话框相关状态 ==========
const showConfirmDialog = ref(false)
const showSuccessDialog = ref(false)
const showErrorDialog = ref(false)
const errorMessage = ref('')
const errorDetails = ref('')
const canRetry = ref(false)
const submitResult = ref<{ report_id: number; risk_level: string }>({
  report_id: 0,
  risk_level: '',
})

// ========== 新增：返回首页对话框状态 ==========
const showGoHomeDialog = ref(false)
const savingProgress = ref(false)

// Toast 相关
const toastVisible = ref(false)
const toastMessage = ref('')
const toastType = ref<'success' | 'error' | 'warning' | 'info'>('info')
const toastIcon = ref('💡')
let toastTimer: ReturnType<typeof setTimeout> | null = null

// --- 计算属性 ---
const answeredCount = computed(() => Object.keys(answers.value).length)
const progressPercentage = computed(
  () => Math.round((answeredCount.value / questions.value.length) * 100) || 0,
)
const formattedTime = computed(() => {
  const minutes = Math.floor(elapsedTime.value / 60)
  const seconds = elapsedTime.value % 60
  return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
})

// 未答题信息
const unansweredInfo = computed(() => {
  const unansweredQuestions = questions.value.filter((q) => answers.value[q.id] === undefined)
  return {
    count: unansweredQuestions.length,
    questions: unansweredQuestions,
  }
})

// 分页相关
const pageNumbers = computed(() => {
  const pages = Math.ceil(questions.value.length / 10)
  return Array.from({ length: pages }, (_, i) => i + 1)
})

// 获取当前题目的安全方法
const getCurrentQuestion = (): Question | undefined => {
  if (questions.value.length === 0) return undefined
  return questions.value[currentIndex.value]
}

// 检查选项是否被选中
const isOptionSelected = (score: number): boolean => {
  const currentQuestion = getCurrentQuestion()
  if (!currentQuestion) return false
  return answers.value[currentQuestion.id] === score
}

// 检查当前题目是否已回答
const hasCurrentQuestionAnswered = (): boolean => {
  const currentQuestion = getCurrentQuestion()
  if (!currentQuestion) return false
  return answers.value[currentQuestion.id] !== undefined
}

// --- [修改] onMounted 生命周期 ---
onMounted(async () => {
  if (!uid) {
    showToast('用户未登录', 'error')
    router.push('/login')
    return
  }

  try {
    // 1. 并行请求：获取题目 + 检查状态(action='check')
    const [questionsRes, startRes] = await Promise.all([
      fetchQuestions(),
      startAssessment(uid, 'check'),
    ])

    // 2. 加载题目
    if (questionsRes.code === 200) {
      questions.value = questionsRes.data.questions || []
    }

    // 3. 处理会话状态
    if (startRes.code === 200) {
      const data = startRes.data as StartResponse

      if (data.is_resumed) {
        tempSessionData.value = data
        showResumeDialog.value = true
      } else {
        initSession(data)
      }
    }
  } catch (error) {
    console.error('初始化测评失败:', error)
    showToast('网络异常，无法加载试卷', 'error')
    loading.value = false
  }
})

// --- [新增] 初始化会话的通用方法 ---
const initSession = (data: StartResponse) => {
  sessionId.value = data.session_id || 0
  answers.value = data.answers_snapshot || {}

  if (data.is_resumed && data.current_progress_index !== undefined) {
    currentIndex.value = Math.min(data.current_progress_index, questions.value.length - 1)
  } else {
    currentIndex.value = 0
  }

  loading.value = false
  startTimer()
}

// --- [新增] 用户选择处理函数 ---

// 选择 1: 继续上次进度
const handleResumeSession = () => {
  if (tempSessionData.value) {
    initSession(tempSessionData.value)
    showToast('已恢复上次进度', 'info')
  }
  showResumeDialog.value = false
}

// 选择 2: 开启新测评
const handleStartNewSession = async () => {
  showResumeDialog.value = false
  loading.value = true

  try {
    const res = await startAssessment(uid, 'new')
    if (res.code === 200) {
      initSession(res.data)
      showToast('已开启全新测评', 'success')
    }
  } catch (e) {
    console.error(e)
    showToast('开启新测评失败', 'error')
    loading.value = false
  }
}

onBeforeUnmount(() => {
  if (timer) clearInterval(timer)
  if (saveTimeout.value) clearTimeout(saveTimeout.value)
  if (toastTimer) clearTimeout(toastTimer)
})

// --- 计时器 ---
const startTimer = () => {
  timer = setInterval(() => {
    elapsedTime.value += 1
  }, 1000)
}

// --- 交互逻辑 ---
const handleSelectOption = async (questionId: number, score: number, optionId: number) => {
  if (questionId === 0) return

  answers.value[questionId] = score

  pulseOptionId.value = optionId
  setTimeout(() => {
    pulseOptionId.value = null
  }, 500)

  debouncedSave()
}

const changeQuestion = (step: number) => {
  const nextIndex = currentIndex.value + step
  if (nextIndex >= 0 && nextIndex < questions.value.length) {
    currentIndex.value = nextIndex
    debouncedSave()
  }
}

const jumpToQuestion = (index: number) => {
  if (index >= 0 && index < questions.value.length) {
    currentIndex.value = index
  }
}

const goToPage = (page: number) => {
  const startIndex = (page - 1) * 10
  if (startIndex < questions.value.length) {
    currentIndex.value = startIndex
  }
}

// 防抖保存
const debouncedSave = () => {
  if (saveTimeout.value) clearTimeout(saveTimeout.value)

  saveTimeout.value = setTimeout(async () => {
    try {
      if (sessionId.value > 0) {
        await saveProgress(sessionId.value, currentIndex.value, answers.value)
      }
    } catch (error) {
      console.warn('保存失败:', error)
    }
  }, 1000)
}

// 获取页面答题状态
const getPageAnsweredStatus = (page: number): boolean => {
  const startIndex = (page - 1) * 10
  const endIndex = Math.min(page * 10, questions.value.length)
  return questions.value
    .slice(startIndex, endIndex)
    .some((q: Question) => answers.value[q.id] !== undefined)
}

// 标记题目
const toggleFlagQuestion = (index: number) => {
  const idx = flaggedQuestions.value.indexOf(index)
  if (idx === -1) {
    flaggedQuestions.value.push(index)
    showToast('题目已标记', 'info')
  } else {
    flaggedQuestions.value.splice(idx, 1)
  }
}

// 滚动到未答题目
const scrollToUnanswered = () => {
  const firstUnanswered = questions.value.findIndex((q: Question) => !answers.value[q.id])
  if (firstUnanswered !== -1) {
    currentIndex.value = firstUnanswered
    showToast(`已跳转到第 ${firstUnanswered + 1} 题`, 'info')
  } else {
    showToast('所有题目已完成', 'success')
  }
}

// 获取分数样式
const getScoreClass = (score: number) => {
  if (score <= 2) return 'score-low'
  if (score <= 3) return 'score-medium'
  return 'score-high'
}

// ========== 提交相关方法 ==========

// 点击提交按钮 - 显示确认对话框
const handleSubmit = () => {
  showConfirmDialog.value = true
}

// 取消提交
const cancelSubmit = () => {
  showConfirmDialog.value = false
}

// 确认提交
const confirmSubmit = async () => {
  submitting.value = true

  try {
    const response = await submitAssessment(sessionId.value)

    if (response.code === 200) {
      showConfirmDialog.value = false
      submitResult.value = {
        report_id: response.data.report_id,
        risk_level: response.data.risk_level || 'good',
      }
      showSuccessDialog.value = true
    } else {
      handleSubmitError(response.code, response.msg, response.data as SubmitErrorData)
    }
  } catch (error: unknown) {
    console.error('提交失败:', error)
    showConfirmDialog.value = false

    if (error && typeof error === 'object' && 'response' in error) {
      const err = error as { response?: { status?: number; data?: SubmitErrorData } }
      const status = err.response?.status || 500
      const data: SubmitErrorData = err.response?.data || {}
      handleSubmitError(status, data.msg || '服务器错误', data)
    } else {
      showErrorMessage('网络连接失败', '请检查您的网络连接后重试', true)
    }
  } finally {
    submitting.value = false
  }
}

// 处理提交错误
const handleSubmitError = (code: number, msg: string, data?: SubmitErrorData) => {
  showConfirmDialog.value = false

  switch (code) {
    case 400:
      if (msg.includes('未完成') || msg.includes('没有答题')) {
        const total = data?.total || questions.value.length
        const answered = data?.answered || answeredCount.value
        const unanswered = total - answered
        showErrorMessage(`还有 ${unanswered} 道题目未完成`, '请继续完成所有题目后再提交', false)

        const firstUnanswered = questions.value.findIndex((q) => answers.value[q.id] === undefined)
        if (firstUnanswered !== -1) {
          setTimeout(() => {
            currentIndex.value = firstUnanswered
          }, 500)
        }
      } else {
        showErrorMessage(msg, '请检查后重试', false)
      }
      break

    case 404:
      showErrorMessage('会话不存在或已过期', '请刷新页面重新开始测评', false)
      break

    case 500:
      showErrorMessage('服务器内部错误', '请稍后重试，如问题持续请联系管理员', true)
      break

    default:
      showErrorMessage(msg || '提交失败', '请稍后重试', true)
  }
}

// 显示错误信息
const showErrorMessage = (message: string, details: string, retry: boolean) => {
  errorMessage.value = message
  errorDetails.value = details
  canRetry.value = retry
  showErrorDialog.value = true
}

// 关闭错误对话框
const closeErrorDialog = () => {
  showErrorDialog.value = false
  errorMessage.value = ''
  errorDetails.value = ''
}

// 重试提交
const retrySubmit = () => {
  closeErrorDialog()
  handleSubmit()
}

// 查看报告
const viewReport = () => {
  showSuccessDialog.value = false
  router.push(`/report/${submitResult.value.report_id}`)
}

// 获取风险等级文本
const getRiskLevelText = (level: string) => {
  const levelMap: Record<string, string> = {
    good: '心理状态良好',
    moderate: '存在一定风险倾向',
    severe: '需要重点关注',
  }
  return levelMap[level] || '评估完成'
}

// 获取风险等级图标
const getRiskIcon = (level: string) => {
  const iconMap: Record<string, string> = {
    good: '😊',
    moderate: '😐',
    severe: '😟',
  }
  return iconMap[level] || '📊'
}

// ========== 新增：返回首页相关方法 ==========

// 点击心灵驿站按钮 - 显示确认对话框
const handleGoHome = () => {
  showGoHomeDialog.value = true
}

// 取消返回首页
const cancelGoHome = () => {
  showGoHomeDialog.value = false
}

// 确认返回首页
const confirmGoHome = async () => {
  savingProgress.value = true

  try {
    // 先保存当前进度
    if (sessionId.value > 0) {
      await saveProgress(sessionId.value, currentIndex.value, answers.value)
    }

    showGoHomeDialog.value = false
    showToast('进度已保存', 'success')

    // 延迟跳转，让用户看到保存成功的提示
    setTimeout(() => {
      router.push('/home')
    }, 500)
  } catch (error) {
    console.error('保存进度失败:', error)
    showToast('保存失败，但仍可返回首页', 'warning')

    // 即使保存失败也允许返回
    setTimeout(() => {
      showGoHomeDialog.value = false
      router.push('/home')
    }, 1000)
  } finally {
    savingProgress.value = false
  }
}

// 直接返回首页（用于无题目时）
const goHome = () => {
  router.push('/home')
}

// ========== Toast 相关方法 ==========
const showToast = (message: string, type: 'success' | 'error' | 'warning' | 'info' = 'info') => {
  if (toastTimer) clearTimeout(toastTimer)

  toastMessage.value = message
  toastType.value = type
  toastIcon.value =
    type === 'success' ? '✅' : type === 'error' ? '❌' : type === 'warning' ? '⚠️' : '💡'
  toastVisible.value = true

  toastTimer = setTimeout(() => {
    toastVisible.value = false
  }, 3000)
}
</script>

<style scoped>
/* ===== 修复滚动问题 - 添加到样式最前面 ===== */
:global(html),
:global(body),
:global(#app) {
  height: auto !important;
  min-height: 100% !important;
  overflow-x: hidden !important;
  overflow-y: visible !important;
}

.assessment-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8f9ff 0%, #f0f7ff 100%);
  position: relative;
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

.floating-icon:nth-child(4) {
  top: 20%;
  left: 10%;
  animation-delay: -2s;
}
.floating-icon:nth-child(5) {
  top: 60%;
  right: 15%;
  animation-delay: -8s;
}
.floating-icon:nth-child(6) {
  bottom: 20%;
  left: 20%;
  animation-delay: -12s;
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

/* 顶部进度条 */
.top-progress-bar {
  height: 4px;
  background: rgba(0, 137, 123, 0.1);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #00897b, #00acc1);
  border-radius: 2px;
  transition: width 0.6s ease;
  position: relative;
}

.progress-fill::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

.progress-info {
  position: absolute;
  right: 20px;
  top: -30px;
  background: white;
  padding: 6px 12px;
  border-radius: 20px;
  box-shadow: 0 4px 12px rgba(0, 137, 123, 0.2);
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #546e7a;
}

.progress-percent {
  font-weight: 700;
  color: #00897b;
  font-size: 14px;
}

/* 页面头部 */
.page-header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(0, 137, 123, 0.1);
  padding: 15px 30px;
  position: fixed;
  top: 4px;
  left: 0;
  right: 0;
  z-index: 999;
}
.header-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  flex-shrink: 0;
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
.home-hint {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #90a4ae;
  font-size: 10px;
  margin: 4px 0 0 0;
  opacity: 0.8;
  transition: all 0.3s ease;
}

.logo-section:hover .home-hint {
  color: #00897b;
  opacity: 1;
}

.hint-arrow {
  font-size: 12px;
  animation: arrowBounce 1.5s infinite ease-in-out;
}

@keyframes arrowBounce {
  0%,
  100% {
    transform: translateX(0);
  }
  50% {
    transform: translateX(-3px);
  }
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
  background: linear-gradient(135deg, #00897b, #00acc1);
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
}

.page-subtitle {
  color: #90a4ae;
  font-size: 13px;
  margin: 6px 0 0 0;
}

.header-right {
  flex-shrink: 0;
}

.session-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: flex-end;
}

.session-badge {
  background: rgba(0, 137, 123, 0.1);
  padding: 6px 12px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
}

.badge-icon {
  font-size: 12px;
}

.timer {
  background: rgba(33, 150, 243, 0.1);
  padding: 6px 12px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #2196f3;
  font-weight: 600;
  animation: pulseTimer 2s infinite;
}

@keyframes pulseTimer {
  0%,
  100% {
    box-shadow: 0 0 0 0 rgba(33, 150, 243, 0.4);
  }
  50% {
    box-shadow: 0 0 0 4px rgba(33, 150, 243, 0);
  }
}

/* 主内容区域 */
.main-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 100px 20px 120px;
  display: flex;
  gap: 25px;
  position: relative;
  z-index: 1;
}

/* 题目区域 */
.question-area {
  flex: 1;
  min-width: 0;
}

.card {
  background: white;
  border-radius: 20px;
  box-shadow: 0 8px 30px rgba(0, 137, 123, 0.1);
  overflow: hidden;
  position: relative;
  border: 1px solid rgba(0, 137, 123, 0.05);
}

.question-card {
  padding: 20px;
  min-height: auto;
  display: flex;
  flex-direction: column;
}

.card-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  overflow: hidden;
}

.wave {
  position: absolute;
  height: 200%;
  width: 200%;
  background: rgba(0, 137, 123, 0.02);
  border-radius: 40%;
  animation: wave 20s infinite linear;
}

.wave-1 {
  top: -50%;
  left: -50%;
  animation-delay: 0s;
}

.wave-2 {
  top: -60%;
  left: -40%;
  animation-delay: -10s;
}

@keyframes wave {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.question-header {
  margin-bottom: 15px;
}

.question-meta {
  margin-bottom: 15px;
}

.question-number-wrapper {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.question-number {
  display: flex;
  align-items: center;
  gap: 6px;
  background: linear-gradient(135deg, #00897b, #00acc1);
  padding: 6px 14px;
  border-radius: 12px;
  color: white;
  font-weight: 700;
}

.number-icon {
  font-size: 14px;
}

.current-num {
  font-size: 20px;
  line-height: 1;
}

.total-num {
  font-size: 14px;
  opacity: 0.8;
}

.progress-indicator {
  display: flex;
  gap: 6px;
}

.progress-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #e0e0e0;
  transition: all 0.3s ease;
}

.progress-dot.active {
  background: #00897b;
  transform: scale(1.2);
}

.question-body {
  background: rgba(0, 137, 123, 0.02);
  border-radius: 12px;
  padding: 15px;
  border: 1px solid rgba(0, 137, 123, 0.1);
}

.question-stem {
  color: #263238;
  font-size: 18px;
  line-height: 1.5;
  margin: 0 0 10px 0;
  font-weight: 600;
}

.stem-text {
  background: linear-gradient(135deg, #263238, #37474f);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.question-tips {
  margin-top: 10px;
}

.tip-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #546e7a;
  font-size: 12px;
  padding: 6px 10px;
  background: rgba(255, 193, 7, 0.1);
  border-radius: 8px;
  border: 1px solid rgba(255, 193, 7, 0.2);
}

/* 选项列表 */
.options-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
  margin-bottom: 15px;
}

.option-item {
  position: relative;
  padding: 12px 15px;
  border: 2px solid rgba(0, 137, 123, 0.1);
  border-radius: 10px;
  background: white;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.option-item:hover {
  border-color: #00897b;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 137, 123, 0.15);
}

.option-item.active {
  border-color: #00897b;
  background: linear-gradient(135deg, rgba(0, 137, 123, 0.05), rgba(0, 137, 123, 0.02));
  transform: translateY(-1px);
  box-shadow: 0 4px 15px rgba(0, 137, 123, 0.2);
}

.option-item.pulse {
  animation: pulse 0.5s ease-out;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(0, 137, 123, 0.4);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(0, 137, 123, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(0, 137, 123, 0);
  }
}

.option-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
  z-index: 1;
}

.option-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.option-circle {
  display: flex;
  align-items: center;
  gap: 15px;
}

.circle-inner {
  width: 18px;
  height: 18px;
  border: 2px solid #90a4ae;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.option-item.active .circle-inner {
  border-color: #00897b;
  transform: scale(1.1);
}

.circle-dot {
  width: 8px;
  height: 8px;
  background: #00897b;
  border-radius: 50%;
  animation: scaleIn 0.3s ease-out;
}

@keyframes scaleIn {
  from {
    transform: scale(0);
  }
  to {
    transform: scale(1);
  }
}

.option-label {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.label-text {
  color: #263238;
  font-size: 14px;
  font-weight: 600;
}

.label-score {
  color: #90a4ae;
  font-size: 11px;
}

.option-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.score-badge {
  background: #00897b;
  color: white;
  padding: 4px 10px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
  animation: fadeIn 0.3s ease-out;
}

.selected-indicator {
  width: 20px;
  height: 20px;
  background: #4caf50;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 12px;
  animation: bounceIn 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

@keyframes bounceIn {
  0% {
    transform: scale(0);
  }
  50% {
    transform: scale(1.2);
  }
  100% {
    transform: scale(1);
  }
}

.option-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
}

.sparkle {
  position: absolute;
  width: 4px;
  height: 4px;
  background: white;
  border-radius: 50%;
  animation: sparkle 1s infinite;
}

.sparkle:nth-child(1) {
  top: 10px;
  left: 20px;
  animation-delay: 0s;
}
.sparkle:nth-child(2) {
  bottom: 10px;
  right: 20px;
  animation-delay: 0.3s;
}

@keyframes sparkle {
  0%,
  100% {
    opacity: 0;
    transform: scale(0);
  }
  50% {
    opacity: 1;
    transform: scale(1);
  }
}

/* 导航按钮 */
.navigation-btns {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 15px;
  margin-top: auto;
  padding-top: 15px;
  border-top: 1px solid rgba(0, 137, 123, 0.1);
}

.nav-btn {
  position: relative;
  padding: 10px 20px;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 110px;
}

.nav-btn.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-content {
  display: flex;
  align-items: center;
  gap: 8px;
  position: relative;
  z-index: 1;
}

.btn-wave {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  transform: translate(-50%, -50%);
  animation: waveExpand 0.6s ease-out;
}

@keyframes waveExpand {
  to {
    width: 300px;
    height: 300px;
    opacity: 0;
  }
}

.prev-btn {
  background: linear-gradient(135deg, #f5f5f5, #e0e0e0);
  color: #546e7a;
}

.prev-btn:hover:not(.disabled) {
  background: linear-gradient(135deg, #e0e0e0, #d0d0d0);
  transform: translateX(-5px);
}

.next-btn {
  background: linear-gradient(135deg, #00897b, #00acc1);
  color: white;
}

.next-btn:hover:not(.disabled) {
  background: linear-gradient(135deg, #00796b, #0097a7);
  transform: translateX(5px);
}

.submit-btn {
  background: linear-gradient(135deg, #ff5722, #ff7043);
  color: white;
  position: relative;
}

.submit-btn:hover:not(.disabled) {
  background: linear-gradient(135deg, #f4511e, #ff5722);
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(255, 87, 34, 0.3);
}

.submit-ring {
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  border: 2px solid transparent;
  border-top-color: #ff5722;
  border-radius: 14px;
  animation: spinRing 1s linear infinite;
}

@keyframes spinRing {
  to {
    transform: rotate(360deg);
  }
}

.page-controls {
  display: flex;
  gap: 8px;
}

.page-btn {
  width: 30px;
  height: 30px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  background: white;
  color: #546e7a;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 600;
  font-size: 12px;
  position: relative;
}

.page-btn:hover {
  border-color: #00897b;
  color: #00897b;
}

.page-btn.active {
  background: #00897b;
  color: white;
  border-color: #00897b;
}

.page-btn.answered::after {
  content: '';
  position: absolute;
  bottom: 2px;
  left: 50%;
  transform: translateX(-50%);
  width: 6px;
  height: 6px;
  background: #4caf50;
  border-radius: 50%;
}

/* 侧边栏 */
.sidebar {
  width: 280px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

/* 统计卡片 */
.stats-card {
  padding: 15px;
}

.stats-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 15px;
}

.stats-icon {
  font-size: 20px;
}

.stats-title {
  color: #263238;
  font-size: 14px;
  margin: 0;
  font-weight: 700;
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 15px;
}

.stat-item {
  background: rgba(0, 137, 123, 0.05);
  border-radius: 10px;
  padding: 10px;
  text-align: center;
  transition: transform 0.3s ease;
}

.stat-item:hover {
  transform: translateY(-3px);
}

.stat-item.total {
  background: rgba(33, 150, 243, 0.1);
  border: 1px solid rgba(33, 150, 243, 0.2);
}
.stat-item.answered {
  background: rgba(76, 175, 80, 0.1);
  border: 1px solid rgba(76, 175, 80, 0.2);
}
.stat-item.remaining {
  background: rgba(255, 152, 0, 0.1);
  border: 1px solid rgba(255, 152, 0, 0.2);
}
.stat-item.accuracy {
  background: rgba(156, 39, 176, 0.1);
  border: 1px solid rgba(156, 39, 176, 0.2);
}

.stat-value {
  font-size: 22px;
  font-weight: 700;
  color: #00897b;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-item.total .stat-value {
  color: #2196f3;
}
.stat-item.answered .stat-value {
  color: #4caf50;
}
.stat-item.remaining .stat-value {
  color: #ff9800;
}
.stat-item.accuracy .stat-value {
  color: #9c27b0;
}

.stat-label {
  font-size: 11px;
  color: #546e7a;
}

.stats-progress {
  margin-top: 15px;
}

.progress-bar-mini {
  height: 6px;
  background: rgba(0, 137, 123, 0.1);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill-mini {
  height: 100%;
  background: linear-gradient(90deg, #00897b, #00acc1);
  border-radius: 3px;
  transition: width 0.6s ease;
}

/* 答题卡 */
.answer-sheet-card {
  padding: 15px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.sheet-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(0, 137, 123, 0.1);
}

.sheet-icon {
  font-size: 18px;
}

.sheet-title {
  color: #263238;
  font-size: 14px;
  margin: 0;
  font-weight: 700;
  flex: 1;
  margin-left: 8px;
}

.sheet-tools {
  display: flex;
  gap: 8px;
}

.tool-btn {
  width: 32px;
  height: 32px;
  border: 1px solid rgba(0, 137, 123, 0.2);
  border-radius: 8px;
  background: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.tool-btn:hover {
  background: rgba(0, 137, 123, 0.1);
  border-color: #00897b;
}

.sheet-container {
  flex: 1;
  overflow-y: auto;
  max-height: 300px;
  padding-right: 5px;
}

.sheet-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 6px;
}

.grid-item {
  width: 100%;
  aspect-ratio: 1;
  border: 1.5px solid #e0e0e0;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  color: #546e7a;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.grid-item:hover {
  border-color: #00897b;
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(0, 137, 123, 0.2);
}

.grid-item.answered {
  background: #e0f2f1;
  color: #00897b;
  border-color: #e0f2f1;
}

.grid-item.current {
  border-color: #00897b;
  box-shadow: 0 0 0 3px rgba(0, 137, 123, 0.2);
  font-weight: 700;
  animation: currentPulse 2s infinite;
}

@keyframes currentPulse {
  0%,
  100% {
    box-shadow: 0 0 0 3px rgba(0, 137, 123, 0.2);
  }
  50% {
    box-shadow: 0 0 0 6px rgba(0, 137, 123, 0);
  }
}

.grid-item.flagged {
  border-color: #ff9800;
  background: rgba(255, 152, 0, 0.1);
}

.item-number {
  font-weight: 600;
  z-index: 1;
}

.item-score {
  position: absolute;
  bottom: 2px;
  right: 2px;
  width: 12px;
  height: 12px;
  border-radius: 3px;
  font-size: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
}

.score-low {
  background: #4caf50;
}
.score-medium {
  background: #ff9800;
}
.score-high {
  background: #f44336;
}

.item-flag {
  position: absolute;
  top: 2px;
  right: 2px;
  font-size: 10px;
  transform: rotate(15deg);
  animation: flagWave 2s infinite;
}

@keyframes flagWave {
  0%,
  100% {
    transform: rotate(15deg);
  }
  50% {
    transform: rotate(25deg);
  }
}

/* 修改：简化后的sheet-footer样式 */
.sheet-footer {
  margin-top: 12px;
  padding-top: 10px;
  border-top: 1px solid rgba(0, 137, 123, 0.1);
}

.sheet-legend {
  display: flex;
  gap: 10px;
  justify-content: center;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 10px;
  color: #546e7a;
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.legend-dot.current {
  background: #00897b;
}
.legend-dot.answered {
  background: #e0f2f1;
}
.legend-dot.flagged {
  background: #ff9800;
}

/* 加载状态 */
.loading-state {
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

.loading-content {
  text-align: center;
  max-width: 400px;
  padding: 40px;
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

.loading-circle:nth-child(1) {
  animation-delay: -0.32s;
}
.loading-circle:nth-child(2) {
  animation-delay: -0.16s;
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
  margin: 0 0 30px 0;
}

.loading-progress {
  height: 4px;
  background: rgba(0, 137, 123, 0.1);
  border-radius: 2px;
  overflow: hidden;
}

.loading-bar {
  height: 100%;
  width: 30%;
  background: linear-gradient(90deg, #00897b, #00acc1);
  border-radius: 2px;
  animation: loadingBar 2s infinite ease-in-out;
}

@keyframes loadingBar {
  0%,
  100% {
    transform: translateX(-100%);
  }
  50% {
    transform: translateX(400%);
  }
}

/* 时间提示 */
.time-hint {
  position: fixed;
  bottom: 30px;
  right: 30px;
  background: rgba(255, 193, 7, 0.95);
  backdrop-filter: blur(10px);
  padding: 12px 20px;
  border-radius: 15px;
  box-shadow: 0 8px 25px rgba(255, 193, 7, 0.3);
  animation: slideIn 0.5s ease-out;
  border: 1px solid rgba(255, 193, 7, 0.2);
  z-index: 100;
}

@keyframes slideIn {
  from {
    transform: translateY(100px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.hint-content {
  display: flex;
  align-items: center;
  gap: 10px;
}

.hint-icon {
  font-size: 18px;
}

.hint-text {
  color: #8a6d3b;
  font-size: 13px;
  font-weight: 600;
}

/* 无题目提示 */
.no-questions {
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

.no-questions-content {
  text-align: center;
  padding: 40px;
}

.no-questions-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.no-questions-title {
  color: #263238;
  font-size: 24px;
  margin: 0 0 10px 0;
}

.no-questions-subtitle {
  color: #90a4ae;
  margin: 0 0 30px 0;
}

.no-questions-btn {
  padding: 12px 30px;
  background: linear-gradient(135deg, #00897b, #00acc1);
  color: white;
  border: none;
  border-radius: 25px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.no-questions-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 25px rgba(0, 137, 123, 0.3);
}

/* ========== 对话框样式 ========== */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.dialog-container {
  background: white;
  border-radius: 24px;
  padding: 30px;
  width: 90%;
  max-width: 420px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.25);
  animation: dialogSlideIn 0.3s ease-out;
}

@keyframes dialogSlideIn {
  from {
    opacity: 0;
    transform: scale(0.9) translateY(20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.dialog-header {
  text-align: center;
  margin-bottom: 20px;
}

.dialog-icon-wrapper {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 15px;
  font-size: 32px;
}

.dialog-icon-wrapper.confirm {
  background: linear-gradient(135deg, rgba(0, 137, 123, 0.1), rgba(0, 172, 193, 0.1));
}

.dialog-icon-wrapper.success {
  background: linear-gradient(135deg, rgba(76, 175, 80, 0.1), rgba(129, 199, 132, 0.1));
  animation: successPulse 2s infinite;
}

@keyframes successPulse {
  0%,
  100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

.dialog-icon-wrapper.error {
  background: linear-gradient(135deg, rgba(244, 67, 54, 0.1), rgba(239, 83, 80, 0.1));
}

/* 新增：返回首页对话框图标样式 */
.dialog-icon-wrapper.home {
  background: linear-gradient(135deg, rgba(0, 137, 123, 0.1), rgba(0, 172, 193, 0.1));
}

.dialog-title {
  color: #263238;
  font-size: 22px;
  margin: 0;
  font-weight: 700;
}

.dialog-body {
  text-align: center;
  margin-bottom: 25px;
}

.dialog-message {
  color: #546e7a;
  font-size: 16px;
  margin: 0 0 15px 0;
  line-height: 1.5;
}

.warning-info {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 152, 0, 0.1);
  padding: 10px 20px;
  border-radius: 25px;
  border: 1px solid rgba(255, 152, 0, 0.2);
}

.warning-icon {
  font-size: 18px;
}

.warning-text {
  color: #e65100;
  font-size: 14px;
  font-weight: 600;
}

/* 新增：保存信息样式 */
.save-info {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  background: linear-gradient(135deg, rgba(76, 175, 80, 0.1), rgba(129, 199, 132, 0.1));
  padding: 12px 20px;
  border-radius: 12px;
  border: 1px solid rgba(76, 175, 80, 0.2);
  margin-bottom: 15px;
}

.save-icon {
  font-size: 20px;
}

.save-text {
  color: #2e7d32;
  font-size: 14px;
  font-weight: 500;
}

/* 新增：进度摘要样式 */
.progress-summary {
  background: rgba(0, 137, 123, 0.05);
  border-radius: 12px;
  padding: 15px;
  border: 1px solid rgba(0, 137, 123, 0.1);
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.summary-item:not(:last-child) {
  border-bottom: 1px dashed rgba(0, 137, 123, 0.1);
}

.summary-label {
  color: #78909c;
  font-size: 14px;
}

.summary-value {
  color: #263238;
  font-size: 14px;
  font-weight: 600;
}

.summary-value.highlight {
  color: #00897b;
  font-size: 16px;
}

.risk-level-badge {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 15px 25px;
  border-radius: 30px;
  font-size: 16px;
  font-weight: 600;
}

.risk-level-badge.good {
  background: linear-gradient(135deg, rgba(76, 175, 80, 0.1), rgba(129, 199, 132, 0.1));
  color: #2e7d32;
  border: 2px solid rgba(76, 175, 80, 0.3);
}

.risk-level-badge.moderate {
  background: linear-gradient(135deg, rgba(255, 193, 7, 0.1), rgba(255, 213, 79, 0.1));
  color: #f57c00;
  border: 2px solid rgba(255, 193, 7, 0.3);
}

.risk-level-badge.severe {
  background: linear-gradient(135deg, rgba(244, 67, 54, 0.1), rgba(239, 83, 80, 0.1));
  color: #c62828;
  border: 2px solid rgba(244, 67, 54, 0.3);
}

.risk-icon {
  font-size: 24px;
}

.error-details {
  margin-top: 10px;
  padding: 12px 20px;
  background: rgba(244, 67, 54, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(244, 67, 54, 0.1);
}

.details-text {
  color: #90a4ae;
  font-size: 14px;
}

.dialog-footer {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.dialog-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 28px;
  border: none;
  border-radius: 25px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 130px;
}

.dialog-btn .btn-icon {
  font-size: 16px;
}

.dialog-btn.cancel {
  background: #f5f5f5;
  color: #546e7a;
}

.dialog-btn.cancel:hover {
  background: #e0e0e0;
  transform: translateY(-2px);
}

.dialog-btn.confirm {
  background: linear-gradient(135deg, #00897b, #00acc1);
  color: white;
}

.dialog-btn.confirm:hover:not(:disabled) {
  background: linear-gradient(135deg, #00796b, #0097a7);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 137, 123, 0.3);
}

.dialog-btn.confirm:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.dialog-btn.primary {
  background: linear-gradient(135deg, #00897b, #00acc1);
  color: white;
  flex: 1;
}

.dialog-btn.primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #00796b, #0097a7);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 137, 123, 0.3);
}

.dialog-btn.primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.dialog-btn.secondary {
  background: #f5f5f5;
  color: #546e7a;
}

.dialog-btn.secondary:hover {
  background: #e0e0e0;
  transform: translateY(-2px);
}

.loading-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Dialog 过渡动画 */
.dialog-fade-enter-active,
.dialog-fade-leave-active {
  transition: all 0.3s ease;
}

.dialog-fade-enter-from,
.dialog-fade-leave-to {
  opacity: 0;
}

.dialog-fade-enter-from .dialog-container,
.dialog-fade-leave-to .dialog-container {
  transform: scale(0.9) translateY(20px);
}

/* ========== Toast 样式 ========== */
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

.toast-container.warning {
  background: linear-gradient(135deg, #ff9800, #ffb74d);
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

/* 响应式设计 */
@media (max-width: 1200px) {
  .main-content {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
    flex-direction: row;
  }

  .stats-card {
    flex: 1;
  }

  .answer-sheet-card {
    flex: 2;
  }
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }

  .session-info {
    align-items: center;
  }

  .navigation-btns {
    flex-direction: column;
  }

  .nav-btn {
    width: 100%;
  }

  .page-controls {
    order: 3;
    width: 100%;
    justify-content: center;
    margin-top: 15px;
  }

  .sidebar {
    flex-direction: column;
  }

  .sheet-grid {
    grid-template-columns: repeat(8, 1fr);
  }

  .dialog-container {
    width: 95%;
    padding: 25px;
  }

  .dialog-footer {
    flex-direction: column;
  }

  .dialog-btn {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .question-card {
    padding: 20px;
  }

  .question-stem {
    font-size: 20px;
  }

  .question-number {
    padding: 8px 15px;
  }

  .current-num {
    font-size: 24px;
  }

  .nav-btn {
    padding: 12px 20px;
    min-width: auto;
  }

  .sheet-grid {
    grid-template-columns: repeat(5, 1fr);
  }

  .time-hint {
    left: 20px;
    right: 20px;
    bottom: 80px;
  }
}

/* --- [新增] 存档弹窗样式 --- */
.dialog-icon-wrapper.info {
  background: linear-gradient(135deg, rgba(33, 150, 243, 0.1), rgba(30, 136, 229, 0.1));
  color: #1e88e5;
}

.dialog-sub-message {
  font-size: 14px;
  color: #78909c;
  margin-top: 10px;
  line-height: 1.5;
}

.dialog-sub-message .note {
  font-size: 12px;
  color: #ff9800;
  display: block;
  margin-top: 5px;
}
</style>
