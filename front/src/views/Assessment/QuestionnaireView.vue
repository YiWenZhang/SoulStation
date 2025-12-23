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
              :class="{ disabled: !hasCurrentQuestionAnswered() || submitting }"
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
            <button class="clear-btn" @click="clearAllAnswers">
              <span class="clear-icon">🗑️</span>
              <span class="clear-text">清空答案</span>
            </button>
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
  type SubmitResponse,
} from '../../api/assessment'

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

// --- 生命周期 ---
onMounted(async () => {
  if (!uid) {
    alert('用户未登录')
    router.push('/login')
    return
  }

  try {
    // 1. 并行请求：获取题目 + 初始化会话
    const [questionsRes, startRes] = await Promise.all([
      fetchQuestions(),
      startAssessment(uid, 'check'), // 默认检查存档
    ])

    // 处理题目响应
    if (questionsRes.code === 200) {
      questions.value = questionsRes.data.questions || []
    }

    // 处理开始测评响应
    if (startRes.code === 200) {
      const data = startRes.data as StartResponse
      sessionId.value = data.session_id || 0
      answers.value = data.answers_snapshot || {} // 恢复答案

      // 如果是恢复存档，跳到上次的位置；如果是新的，从0开始
      if (data.is_resumed && data.current_progress_index !== undefined) {
        currentIndex.value = Math.min(data.current_progress_index, questions.value.length - 1)
        // 可以加个 Toast 提示用户: "已为您恢复上次的答题进度"
      }
    }

    // 3. 启动计时器
    startTimer()
  } catch (error) {
    console.error('初始化测评失败:', error)
    alert('网络异常，无法加载试卷')
  } finally {
    loading.value = false
  }
})

onBeforeUnmount(() => {
  if (timer) clearInterval(timer)
  if (saveTimeout.value) clearTimeout(saveTimeout.value)
})

// --- 计时器 ---
const startTimer = () => {
  timer = setInterval(() => {
    elapsedTime.value += 1
  }, 1000)
}

// --- 交互逻辑 ---
const handleSelectOption = async (questionId: number, score: number, optionId: number) => {
  if (questionId === 0) return // 无效的questionId

  // 1. 更新本地状态
  answers.value[questionId] = score

  // 2. 触发脉冲效果
  pulseOptionId.value = optionId
  setTimeout(() => {
    pulseOptionId.value = null
  }, 500)

  // 3. 自动保存
  debouncedSave()
}

const changeQuestion = (step: number) => {
  const nextIndex = currentIndex.value + step
  if (nextIndex >= 0 && nextIndex < questions.value.length) {
    currentIndex.value = nextIndex
    // 自动保存
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
    showToast('题目已标记')
  } else {
    flaggedQuestions.value.splice(idx, 1)
  }
}

// 滚动到未答题目
const scrollToUnanswered = () => {
  const firstUnanswered = questions.value.findIndex((q: Question) => !answers.value[q.id])
  if (firstUnanswered !== -1) {
    currentIndex.value = firstUnanswered
    showToast(`已跳转到第 ${firstUnanswered + 1} 题`)
  } else {
    showToast('所有题目已完成')
  }
}

// 清空所有答案
const clearAllAnswers = () => {
  if (confirm('确定要清空所有答案吗？这个操作不可撤销。')) {
    answers.value = {}
    flaggedQuestions.value = []
    currentIndex.value = 0
    showToast('已清空所有答案')
  }
}

// 获取分数样式
const getScoreClass = (score: number) => {
  if (score <= 2) return 'score-low'
  if (score <= 3) return 'score-medium'
  return 'score-high'
}

// 提交试卷
const handleSubmit = async () => {
  // 完整性校验
  const unansweredCount = questions.value.length - answeredCount.value
  if (unansweredCount > 0) {
    const confirmSubmit = window.confirm(`还有 ${unansweredCount} 道题未完成，是否确认提交？`)
    if (!confirmSubmit) return
  }

  submitting.value = true
  try {
    const response = await submitAssessment(sessionId.value)

    if (response.code === 200) {
      const data = response.data as SubmitResponse
      if (data.report_id) {
        showToast('提交成功！正在生成报告...')

        // 跳转到报告页面
        setTimeout(() => {
          router.push(`/report/${data.report_id}`)
        }, 1500)
      }
    } else if (response.code === 400) {
      // 题目未答完的错误
      const data = response.data as SubmitResponse
      const total = data.total || 0
      const answered = data.answered || 0
      const unanswered = total - answered
      showToast(`还有 ${unanswered} 道题目未完成，请继续作答`)

      // 滚动到第一个未答题目
      const firstUnanswered = questions.value.find((q) => !answers.value[q.id])
      if (firstUnanswered) {
        const index = questions.value.findIndex((q) => q.id === firstUnanswered.id)
        currentIndex.value = index
      }
    } else {
      showToast('提交失败: ' + (response.msg || '未知错误'))
    }
  } catch (error) {
    console.error('提交失败:', error)
    showToast('提交过程中发生错误')
  } finally {
    submitting.value = false
  }
}

// 显示提示
const showToast = (message: string) => {
  // 这里可以集成一个Toast组件，暂时用alert代替
  alert(message)
}

// 返回首页
const goHome = () => {
  if (confirm('返回首页？您的进度已自动保存。')) {
    router.push('/home')
  }
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
  /* 移除 overflow 属性 */
}

/* 背景装饰 */
.background-decoration {
  position: fixed; /* 保持 fixed */
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
  position: fixed; /* 改为 fixed，始终在顶部 */
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
/* 确保页面头部固定 */
.page-header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(0, 137, 123, 0.1);
  padding: 15px 30px;
  position: fixed; /* 改为 fixed */
  top: 4px; /* 在进度条下方 */
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
/* 调整主内容区域的位置，避免被固定头部遮挡 */
.main-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 100px 20px 120px; /* 顶部留出头部空间，底部留出快捷导航空间 */
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
  min-height: auto; /* 移除最小高度限制 */
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

/* 选项圆圈 */
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

/* 选中指示器 */
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

/* 导航按钮 - 缩小尺寸 */
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

/* 分页按钮 */
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

/* 确保侧边栏不会限制滚动 */
/* ===== 侧边栏调整 ===== */
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

.sheet-footer {
  margin-top: 12px;
  padding-top: 10px;
  border-top: 1px solid rgba(0, 137, 123, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sheet-legend {
  display: flex;
  gap: 10px;
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

.clear-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  background: rgba(244, 67, 54, 0.1);
  color: #f44336;
  border: 1px solid rgba(244, 67, 54, 0.2);
  border-radius: 8px;
  cursor: pointer;
  font-size: 11px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.clear-btn:hover {
  background: rgba(244, 67, 54, 0.2);
  transform: translateY(-2px);
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
  bottom: 30px; /* 调整位置，避免与快捷导航重叠 */
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

  .quick-nav {
    bottom: 10px;
  }

  .nav-buttons {
    flex-wrap: wrap;
    justify-content: center;
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
</style>
