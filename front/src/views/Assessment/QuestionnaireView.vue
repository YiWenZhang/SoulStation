<template>
  <div class="assessment-container">
    <header class="page-header">
      <div class="header-content">
        <h1 class="page-title">🧠 心理健康专业量表测评 (SCL-90)</h1>
        <div class="progress-info">
          进度: <span class="highlight">{{ answeredCount }}</span> / {{ questions.length }}
        </div>
      </div>
    </header>

    <div class="main-content" v-if="!loading">
      <div class="question-area">
        <div class="card question-card" v-if="currentQuestion">
          <div class="question-header">
            <span class="question-index">Q{{ currentIndex + 1 }}</span>
            <h2 class="question-stem">{{ currentQuestion.stem }}</h2>
          </div>

          <div class="options-list">
            <div
              v-for="option in currentQuestion.options"
              :key="option.id"
              class="option-item"
              :class="{ active: answers[currentQuestion.id] === option.score }"
              @click="handleSelectOption(currentQuestion.id, option.score)"
            >
              <div class="radio-circle"></div>
              <span class="option-label">{{ option.label }}</span>
            </div>
          </div>

          <div class="navigation-btns">
            <button class="nav-btn prev" :disabled="currentIndex === 0" @click="changeQuestion(-1)">
              上一题
            </button>

            <button
              v-if="currentIndex < questions.length - 1"
              class="nav-btn next"
              @click="changeQuestion(1)"
            >
              下一题
            </button>

            <button v-else class="nav-btn submit" :disabled="submitting" @click="handleSubmit">
              {{ submitting ? '提交中...' : '提交试卷' }}
            </button>
          </div>
        </div>
      </div>

      <aside class="sidebar">
        <div class="card answer-sheet-card">
          <h3 class="sheet-title">答题卡</h3>
          <div class="sheet-grid">
            <button
              v-for="(q, index) in questions"
              :key="q.id"
              class="grid-item"
              :class="{
                answered: answers[q.id] !== undefined,
                current: currentIndex === index,
              }"
              @click="jumpToQuestion(index)"
            >
              {{ index + 1 }}
            </button>
          </div>

          <div class="sheet-legend">
            <div class="legend-item"><span class="dot current"></span>当前</div>
            <div class="legend-item"><span class="dot answered"></span>已答</div>
            <div class="legend-item"><span class="dot unanswer"></span>未答</div>
          </div>
        </div>
      </aside>
    </div>

    <div v-else class="loading-state">
      <div class="spinner"></div>
      <p>正在加载试卷...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  startAssessment,
  fetchQuestions,
  saveProgress,
  submitAssessment,
  type Question,
} from '../../api/assessment'

const router = useRouter()
const uid = parseInt(localStorage.getItem('uid') || '0')

// --- 状态 ---
const loading = ref(true)
const submitting = ref(false)
const sessionId = ref(0)
const questions = ref<Question[]>([])
const currentIndex = ref(0)
const answers = ref<Record<string, number>>({}) // Map<QuestionID, Score>

// --- 计算属性 ---
const currentQuestion = computed(() => questions.value[currentIndex.value])

const answeredCount = computed(() => Object.keys(answers.value).length)

// --- 初始化逻辑 ---
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

    if (questionsRes.code === 200) {
      questions.value = questionsRes.data.questions
    }

    if (startRes.code === 200) {
      const data = startRes.data
      sessionId.value = data.session_id
      answers.value = data.answers_snapshot || {} // 恢复答案

      // 如果是恢复存档，跳到上次的位置；如果是新的，从0开始
      if (data.is_resumed) {
        currentIndex.value = Math.min(data.current_progress_index, questions.value.length - 1)
        // 可以加个 Toast 提示用户: "已为您恢复上次的答题进度"
      }
    }
  } catch (error) {
    console.error('初始化测评失败:', error)
    alert('网络异常，无法加载试卷')
  } finally {
    loading.value = false
  }
})

// --- 交互逻辑 ---

// 选择答案
const handleSelectOption = async (questionId: number, score: number) => {
  // 1. 更新本地状态
  answers.value = { ...answers.value, [questionId]: score }

  // 2. 自动跳转下一题 (提升体验，可选)
  // setTimeout(() => {
  //   if (currentIndex.value < questions.value.length - 1) {
  //     changeQuestion(1)
  //   }
  // }, 300)
}

// 切换题目 (包含自动保存)
const changeQuestion = async (step: number) => {
  const nextIndex = currentIndex.value + step
  if (nextIndex >= 0 && nextIndex < questions.value.length) {
    // 切换前保存进度 (静默保存，不阻塞UI)
    saveCurrentProgress()

    currentIndex.value = nextIndex
  }
}

// 跳转题目 (答题卡)
const jumpToQuestion = (index: number) => {
  saveCurrentProgress()
  currentIndex.value = index
}

// 调用保存接口
const saveCurrentProgress = async () => {
  const currentQuestionItem = questions.value[currentIndex.value]

  // 1. 卫语句：确保题目存在，如果 currentQuestionItem 为空直接返回
  if (!currentQuestionItem) return

  // 2. 获取 ID
  const currentQId = currentQuestionItem.id

  // 3. 关键修复：将 ID 转为 string 再去访问 answers
  // 因为 answers 定义为 Record<string, number>，必须用 string 做索引
  // 这里的 String() 同时也保证了它绝对不会是 undefined
  const currentScore = answers.value[String(currentQId)]

  // 4. 构建 payload，确保 key 也是 string
  const payload = currentScore ? { [String(currentQId)]: currentScore } : {}

  try {
    // 自动保存
    await saveProgress(sessionId.value, currentIndex.value, payload)
  } catch (error) {
    // 捕获错误时不处理，以免打扰用户
    console.warn('进度自动保存失败', error)
  }
}

// 提交试卷
const handleSubmit = async () => {
  // 1. 完整性校验
  const unansweredCount = questions.value.length - answeredCount.value
  if (unansweredCount > 0) {
    const confirm = window.confirm(
      `还有 ${unansweredCount} 道题未完成，确定要提交吗？(未完成可能无法生成报告)`,
    )
    if (!confirm) return
  }

  submitting.value = true
  try {
    const res = await submitAssessment(sessionId.value)

    if (res.code === 200) {
      // 成功：跳转报告页
      router.push(`/report/${res.data.report_id}`)
    } else if (res.code === 400) {
      // 失败：题目没做完
      alert(res.msg || '请完成所有题目后再提交')
    } else {
      alert('提交失败: ' + res.msg)
    }
  } catch (error) {
    console.error(error)
    alert('提交过程中发生错误')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.assessment-container {
  min-height: 100vh;
  background-color: #f5f7fa;
  display: flex;
  flex-direction: column;
}

/* 顶部 */
.page-header {
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  padding: 0 20px;
  height: 60px;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  height: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  font-size: 18px;
  color: #333;
  margin: 0;
}

.highlight {
  color: #00897b;
  font-weight: bold;
  font-size: 1.2em;
}

/* 主布局 */
.main-content {
  flex: 1;
  display: flex;
  max-width: 1200px;
  width: 100%;
  margin: 20px auto;
  gap: 20px;
  padding: 0 20px;
  box-sizing: border-box;
}

.card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

/* 左侧答题区 */
.question-area {
  flex: 1;
  min-width: 0; /* 防止flex子项溢出 */
}

.question-card {
  padding: 40px;
  min-height: 500px;
  display: flex;
  flex-direction: column;
}

.question-header {
  margin-bottom: 30px;
}

.question-index {
  display: inline-block;
  background: #e0f2f1;
  color: #00897b;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 10px;
}

.question-stem {
  font-size: 22px;
  color: #2c3e50;
  line-height: 1.5;
  margin: 0;
}

.options-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
  flex: 1;
}

.option-item {
  display: flex;
  align-items: center;
  padding: 15px 20px;
  border: 2px solid #eee;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.option-item:hover {
  border-color: #b2dfdb;
  background: #f0fcfc;
}

.option-item.active {
  border-color: #00897b;
  background: #e0f2f1;
}

.radio-circle {
  width: 18px;
  height: 18px;
  border: 2px solid #ccc;
  border-radius: 50%;
  margin-right: 15px;
  position: relative;
}

.option-item.active .radio-circle {
  border-color: #00897b;
}

.option-item.active .radio-circle::after {
  content: '';
  position: absolute;
  top: 3px;
  left: 3px;
  width: 8px;
  height: 8px;
  background: #00897b;
  border-radius: 50%;
}

.navigation-btns {
  margin-top: 40px;
  display: flex;
  justify-content: space-between;
}

.nav-btn {
  padding: 10px 30px;
  border-radius: 8px;
  border: none;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s;
}

.nav-btn.prev {
  background: #f5f5f5;
  color: #666;
}

.nav-btn.prev:hover:not(:disabled) {
  background: #e0e0e0;
}

.nav-btn.prev:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.nav-btn.next {
  background: #00897b;
  color: white;
  margin-left: auto; /* 靠右 */
}

.nav-btn.next:hover {
  background: #00796b;
}

.nav-btn.submit {
  background: #d84315; /* 醒目的提交色 */
  color: white;
  margin-left: auto;
}

/* 右侧答题卡 */
.sidebar {
  width: 300px;
  flex-shrink: 0;
}

.answer-sheet-card {
  padding: 20px;
  position: sticky;
  top: 80px; /* 随滚动固定 */
}

.sheet-title {
  font-size: 16px;
  margin: 0 0 20px 0;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.sheet-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 10px;
  max-height: 400px;
  overflow-y: auto;
  padding-right: 5px; /* 防止滚动条遮挡 */
}

.grid-item {
  width: 100%;
  aspect-ratio: 1;
  border: 1px solid #e0e0e0;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: #666;
  transition: all 0.2s;
}

.grid-item:hover {
  border-color: #00897b;
}

.grid-item.answered {
  background: #e0f2f1;
  color: #00897b;
  border-color: #e0f2f1;
}

.grid-item.current {
  border-color: #00897b;
  box-shadow: 0 0 0 2px rgba(0, 137, 123, 0.2);
  font-weight: bold;
}

.sheet-legend {
  margin-top: 20px;
  display: flex;
  justify-content: space-around;
  font-size: 12px;
  color: #666;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.dot.current {
  border: 2px solid #00897b;
  box-sizing: border-box;
}
.dot.answered {
  background: #e0f2f1;
}
.dot.unanswer {
  border: 1px solid #ccc;
  background: white;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .main-content {
    flex-direction: column-reverse;
  }

  .sidebar {
    width: 100%;
  }

  .answer-sheet-card {
    position: static;
  }

  .sheet-grid {
    grid-template-columns: repeat(8, 1fr);
  }
}
</style>
