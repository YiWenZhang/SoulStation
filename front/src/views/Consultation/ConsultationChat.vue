<template>
  <div class="chat-page">
    <!-- 动态背景 -->
    <div class="background-decoration">
      <div class="gradient-orb orb-1"></div>
      <div class="gradient-orb orb-2"></div>
      <div class="gradient-orb orb-3"></div>
      <div class="floating-shapes">
        <div class="shape shape-1">💬</div>
        <div class="shape shape-2">🧠</div>
        <div class="shape shape-3">💡</div>
        <div class="shape shape-4">🌿</div>
      </div>
      <div class="grid-pattern"></div>
    </div>

    <!-- 聊天容器 -->
    <div class="chat-container">
      <!-- 顶部导航 -->
      <header class="chat-header">
        <div class="header-left">
          <button class="back-btn" @click="goBack">
            <span class="back-icon">←</span>
            <span class="back-text">返回</span>
          </button>
        </div>

        <div class="header-center">
          <div class="ai-status">
            <div class="status-avatar">
              <span class="avatar-emoji">🤖</span>
              <span class="status-dot" :class="{ active: status === 'ongoing' }"></span>
            </div>
            <div class="status-info">
              <h1 class="title">AI 深度问诊</h1>
              <p class="subtitle">
                <span v-if="status === 'ongoing'" class="online-status">
                  <span class="pulse-dot"></span>
                  正在对话中
                </span>
                <span v-else class="offline-status">对话已结束</span>
              </p>
            </div>
          </div>
        </div>

        <div class="header-right">
          <button
            v-if="status === 'ongoing'"
            class="action-btn finish-btn"
            @click="showConfirmDialog = true"
          >
            <span class="btn-icon">✓</span>
            <span class="btn-text">结束并生成报告</span>
          </button>
          <button v-else class="action-btn report-btn" @click="showReportDialog = true">
            <span class="btn-icon">📋</span>
            <span class="btn-text">查看报告</span>
          </button>
        </div>
      </header>

      <!-- 聊天内容区 -->
      <div class="chat-content" ref="chatRef">
        <!-- 加载状态 -->
        <div v-if="loading && messages.length === 0" class="loading-wrapper">
          <div class="loading-animation">
            <div class="loading-brain">🧠</div>
            <div class="loading-rings">
              <div class="ring ring-1"></div>
              <div class="ring ring-2"></div>
              <div class="ring ring-3"></div>
            </div>
          </div>
          <h3 class="loading-title">AI 正在分析您的测评报告</h3>
          <p class="loading-subtitle">正在准备病历信息，请稍候...</p>
          <div class="loading-progress">
            <div class="progress-bar">
              <div class="progress-fill"></div>
            </div>
          </div>
        </div>

        <!-- 欢迎提示 -->
        <div v-if="!loading && messages.length > 0" class="welcome-tip">
          <div class="tip-icon">💡</div>
          <div class="tip-content">
            <strong>温馨提示：</strong>
            请详细描述您的症状和感受，AI 将根据您的测评报告进行深入分析。
          </div>
        </div>

        <!-- 消息列表 -->
        <TransitionGroup name="message-fade" tag="div" class="messages-wrapper">
          <div v-for="(msg, index) in messages" :key="index" class="message-row" :class="msg.role">
            <div class="avatar-wrapper">
              <div class="avatar" :class="msg.role">
                <span v-if="msg.role === 'ai'">🤖</span>
                <img v-else-if="userAvatar" :src="userAvatar" alt="用户头像" />
                <span v-else>👤</span>
              </div>
              <div class="avatar-glow"></div>
            </div>

            <div class="message-content">
              <div class="message-header">
                <span class="sender-name">{{ msg.role === 'ai' ? 'AI 咨询师' : '我' }}</span>
                <span class="message-time">{{ getCurrentTime() }}</span>
              </div>
              <div class="message-bubble" :class="msg.role">
                <div
                  v-if="msg.role === 'ai'"
                  class="markdown-body"
                  v-html="renderMarkdown(msg.content)"
                ></div>
                <div v-else class="user-text">{{ msg.content }}</div>
              </div>
            </div>
          </div>
        </TransitionGroup>

        <!-- AI 正在输入提示 -->
        <Transition name="typing-fade">
          <div v-if="sending" class="typing-indicator">
            <div class="avatar-wrapper">
              <div class="avatar ai">🤖</div>
            </div>
            <div class="typing-bubble">
              <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
              <span class="typing-text">AI 正在思考...</span>
            </div>
          </div>
        </Transition>

        <div class="scroll-anchor"></div>
      </div>

      <!-- 输入区域 -->
      <div class="chat-footer" v-if="status === 'ongoing'">
        <div class="input-container">
          <div class="input-wrapper">
            <textarea
              v-model="inputMessage"
              placeholder="请描述您的症状或感受，按 Enter 发送..."
              rows="3"
              @keydown.enter.exact.prevent="handleSend"
              @keydown.enter.shift.exact="handleNewLine"
              class="message-input"
            ></textarea>
            <div class="input-tools">
              <span class="char-count">{{ inputMessage.length }}/500</span>
            </div>
          </div>
          <button
            class="send-btn"
            @click="handleSend"
            :disabled="!inputMessage.trim() || sending"
            :class="{ active: inputMessage.trim() && !sending }"
          >
            <span v-if="!sending" class="send-icon">
              <svg viewBox="0 0 24 24" fill="none">
                <path
                  d="M22 2L11 13M22 2L15 22L11 13M22 2L2 9L11 13"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>
            </span>
            <span v-else class="sending-spinner"></span>
          </button>
        </div>
        <div class="footer-tips">
          <span class="tip-item"> <kbd>Enter</kbd> 发送 </span>
          <span class="tip-item"> <kbd>Shift</kbd> + <kbd>Enter</kbd> 换行 </span>
        </div>
      </div>

      <!-- 对话已结束提示 -->
      <div class="chat-footer ended" v-else>
        <div class="ended-content">
          <div class="ended-icon">✅</div>
          <div class="ended-text">
            <h4>问诊已完成</h4>
            <p>AI 已根据对话生成诊断报告</p>
          </div>
          <button class="view-report-btn" @click="showReportDialog = true">
            <span class="btn-icon">📋</span>
            <span>查看完整报告</span>
          </button>
        </div>
      </div>
    </div>

    <!-- ========== 确认结束弹窗 ========== -->
    <Teleport to="body">
      <Transition name="confirm-fade">
        <div
          v-if="showConfirmDialog"
          class="confirm-overlay"
          @click.self="showConfirmDialog = false"
        >
          <div class="confirm-modal">
            <!-- 装饰背景 -->
            <div class="modal-decoration">
              <div class="decoration-circle circle-1"></div>
              <div class="decoration-circle circle-2"></div>
            </div>

            <!-- 弹窗头部 -->
            <div class="confirm-header">
              <div class="confirm-icon-wrapper">
                <div class="confirm-icon">
                  <span class="icon-emoji">🏁</span>
                </div>
                <div class="icon-ring"></div>
              </div>
              <h3 class="confirm-title">确认结束问诊？</h3>
              <p class="confirm-subtitle">请确认是否结束当前对话</p>
            </div>

            <!-- 弹窗内容 -->
            <div class="confirm-body">
              <div class="info-card">
                <div class="info-icon">📊</div>
                <div class="info-content">
                  <h4>AI 将生成诊断报告</h4>
                  <p>
                    根据您提供的信息，AI
                    将综合分析并生成一份详细的心理诊断报告，包含评估结果和专业建议。
                  </p>
                </div>
              </div>

              <div class="stats-row">
                <div class="stat-item">
                  <span class="stat-icon">💬</span>
                  <span class="stat-value">{{ messages.length }}</span>
                  <span class="stat-label">对话轮数</span>
                </div>
                <div class="stat-divider"></div>
                <div class="stat-item">
                  <span class="stat-icon">⏱️</span>
                  <span class="stat-value">{{ getSessionDuration() }}</span>
                  <span class="stat-label">问诊时长</span>
                </div>
              </div>

              <div class="warning-tip">
                <span class="warning-icon">💡</span>
                <span class="warning-text">结束后将无法继续当前对话，但您可以随时发起新的问诊</span>
              </div>
            </div>

            <!-- 弹窗底部按钮 -->
            <div class="confirm-footer">
              <button class="confirm-btn cancel" @click="showConfirmDialog = false">
                <span class="btn-icon">💬</span>
                <span>继续问诊</span>
              </button>
              <button class="confirm-btn submit" @click="handleConfirmFinish" :disabled="finishing">
                <span v-if="!finishing" class="btn-content">
                  <span class="btn-icon">✓</span>
                  <span>确定结束</span>
                </span>
                <span v-else class="btn-loading">
                  <span class="spinner"></span>
                  <span>生成报告中...</span>
                </span>
              </button>
            </div>

            <!-- 关闭按钮 -->
            <button class="close-btn" @click="showConfirmDialog = false">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M18 6L6 18M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- ========== 报告弹窗 ========== -->
    <Teleport to="body">
      <Transition name="modal-fade">
        <div v-if="showReportDialog" class="modal-overlay" @click.self="showReportDialog = false">
          <div class="report-modal">
            <div class="modal-header">
              <div class="modal-title">
                <span class="title-icon">🩺</span>
                <span>AI 问诊病历报告</span>
              </div>
              <button class="close-btn" @click="showReportDialog = false">
                <span>×</span>
              </button>
            </div>
            <div class="modal-body">
              <div class="report-content markdown-body" v-html="renderMarkdown(finalReport)"></div>
            </div>
            <div class="modal-footer">
              <button class="modal-btn secondary" @click="showReportDialog = false">
                留在页面
              </button>
              <button class="modal-btn primary" @click="viewHistory">
                <span class="btn-icon">📚</span>
                去历史档案查看
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { startConsultation, chatConsultation, finishConsultation } from '@/api/ai'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

const route = useRoute()
const router = useRouter()
const reportId = route.params.reportId as string

const goBack = () => router.back()
const viewHistory = () => router.push('/history')

interface Message {
  role: 'user' | 'ai'
  content: string
}

const messages = ref<Message[]>([])
const inputMessage = ref('')
const loading = ref(true)
const sending = ref(false)
const finishing = ref(false)
const status = ref<'ongoing' | 'finished'>('ongoing')
const consultationId = ref<number>(0)
const userAvatar = localStorage.getItem('avatar_url') || ''
const sessionStartTime = ref<Date>(new Date())

const showConfirmDialog = ref(false)
const showReportDialog = ref(false)
const finalReport = ref('')

// 获取当前时间
const getCurrentTime = () => {
  const now = new Date()
  return now.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

// 获取问诊时长
const getSessionDuration = () => {
  const now = new Date()
  const diff = Math.floor((now.getTime() - sessionStartTime.value.getTime()) / 1000)
  const minutes = Math.floor(diff / 60)
  const seconds = diff % 60
  return `${minutes}分${seconds}秒`
}

// Markdown 渲染
const renderMarkdown = (text: string) => {
  if (!text) return ''
  marked.setOptions({ breaks: true, gfm: true })
  return DOMPurify.sanitize(marked.parse(text) as string)
}

// 处理换行
const handleNewLine = (e: KeyboardEvent) => {
  const target = e.target as HTMLTextAreaElement
  const start = target.selectionStart
  const end = target.selectionEnd
  inputMessage.value =
    inputMessage.value.substring(0, start) + '\n' + inputMessage.value.substring(end)
  nextTick(() => {
    target.selectionStart = target.selectionEnd = start + 1
  })
}

// 自动滚动
const chatRef = ref<HTMLElement | null>(null)
const scrollToBottom = async () => {
  await nextTick()
  if (chatRef.value) {
    chatRef.value.scrollTo({
      top: chatRef.value.scrollHeight,
      behavior: 'smooth',
    })
  }
}

// 1. 初始化发起问诊
const initConsultation = async () => {
  sessionStartTime.value = new Date()
  try {
    consultationId.value = 0
    const res = await startConsultation(reportId)
    consultationId.value = res.consultation_id
    messages.value.push({ role: 'ai', content: res.message })
    loading.value = false
    scrollToBottom()
  } catch (error) {
    console.error('无法启动 AI 问诊服务', error)
    ElMessage.error('问诊初始化失败，请重试')
    loading.value = false
  }
}

// 2. 发送对话消息
const handleSend = async () => {
  const content = inputMessage.value.trim()
  if (!content || sending.value) return

  messages.value.push({ role: 'user', content })
  inputMessage.value = ''
  scrollToBottom()
  sending.value = true

  try {
    const res = await chatConsultation(consultationId.value, content)
    messages.value.push({ role: 'ai', content: res.message })

    if (res.status === 'finished') {
      status.value = 'finished'
      finalReport.value = res.report || ''
      showReportDialog.value = true
      ElMessage.success('问诊已完成，报告已生成')
    }

    scrollToBottom()
  } catch (error) {
    console.error('对话失败', error)
    ElMessage.error('发送失败，请检查网络')
  } finally {
    sending.value = false
  }
}

// 3. 确认结束问诊
const handleConfirmFinish = async () => {
  finishing.value = true
  try {
    const res = await finishConsultation(consultationId.value)
    status.value = 'finished'
    finalReport.value = res.report || ''
    showConfirmDialog.value = false
    showReportDialog.value = true
    messages.value.push({
      role: 'ai',
      content:
        '**[系统消息]** 对话已结束，感谢您的信任。您可以查看上方生成的完整诊断报告。如有需要，可随时发起新的问诊。',
    })
    scrollToBottom()
  } catch (error) {
    console.error('结束问诊失败', error)
    ElMessage.error('结束问诊失败，请重试')
  } finally {
    finishing.value = false
  }
}

onMounted(() => {
  console.log('当前路由获取的报告ID:', reportId)
  initConsultation()
})
</script>

<style scoped>
/* ============ 页面容器 ============ */
.chat-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8f9ff 0%, #f0f7ff 50%, #e8f5e9 100%);
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

/* ============ 动态背景 ============ */
.background-decoration {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
}

.gradient-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.5;
  animation: floatOrb 20s ease-in-out infinite;
}

.orb-1 {
  width: 400px;
  height: 400px;
  background: linear-gradient(135deg, #a5d6a7 0%, #81d4fa 100%);
  top: -100px;
  right: -100px;
}

.orb-2 {
  width: 300px;
  height: 300px;
  background: linear-gradient(135deg, #c5e1a5 0%, #b2dfdb 100%);
  bottom: 10%;
  left: -80px;
  animation-delay: -7s;
}

.orb-3 {
  width: 250px;
  height: 250px;
  background: linear-gradient(135deg, #b2ebf2 0%, #c8e6c9 100%);
  top: 50%;
  right: 20%;
  animation-delay: -14s;
}

@keyframes floatOrb {
  0%,
  100% {
    transform: translate(0, 0) scale(1);
  }
  25% {
    transform: translate(30px, -30px) scale(1.05);
  }
  50% {
    transform: translate(-20px, 20px) scale(0.95);
  }
  75% {
    transform: translate(20px, 30px) scale(1.02);
  }
}

.floating-shapes {
  position: absolute;
  inset: 0;
}

.shape {
  position: absolute;
  font-size: 24px;
  opacity: 0.15;
  animation: shapeFloat 18s ease-in-out infinite;
}

.shape-1 {
  top: 15%;
  left: 10%;
}
.shape-2 {
  top: 60%;
  right: 8%;
  animation-delay: -5s;
}
.shape-3 {
  bottom: 25%;
  left: 15%;
  animation-delay: -10s;
}
.shape-4 {
  top: 30%;
  right: 25%;
  animation-delay: -15s;
}

@keyframes shapeFloat {
  0%,
  100% {
    transform: translateY(0) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(10deg);
  }
}

.grid-pattern {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(0, 0, 0, 0.02) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 0, 0, 0.02) 1px, transparent 1px);
  background-size: 50px 50px;
}

/* ============ 聊天容器 ============ */
.chat-container {
  width: 100%;
  max-width: 1000px;
  height: 90vh;
  max-height: 800px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 24px;
  box-shadow:
    0 25px 80px rgba(0, 137, 123, 0.12),
    0 0 0 1px rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
  z-index: 1;
  animation: containerAppear 0.6s ease-out;
}

@keyframes containerAppear {
  from {
    opacity: 0;
    transform: translateY(30px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* ============ 顶部导航 ============ */
.chat-header {
  padding: 16px 24px;
  background: rgba(255, 255, 255, 0.9);
  border-bottom: 1px solid rgba(0, 137, 123, 0.08);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  background: rgba(0, 137, 123, 0.08);
  border: none;
  border-radius: 12px;
  color: #00897b;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.back-btn:hover {
  background: rgba(0, 137, 123, 0.15);
  transform: translateX(-3px);
}

.back-icon {
  font-size: 18px;
  transition: transform 0.3s;
}

.back-btn:hover .back-icon {
  transform: translateX(-3px);
}

.ai-status {
  display: flex;
  align-items: center;
  gap: 14px;
}

.status-avatar {
  position: relative;
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #00897b, #26a69a);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 15px rgba(0, 137, 123, 0.3);
}

.avatar-emoji {
  font-size: 26px;
}

.status-dot {
  position: absolute;
  bottom: -2px;
  right: -2px;
  width: 14px;
  height: 14px;
  background: #bdbdbd;
  border: 3px solid white;
  border-radius: 50%;
  transition: background 0.3s;
}

.status-dot.active {
  background: #4caf50;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%,
  100% {
    box-shadow: 0 0 0 0 rgba(76, 175, 80, 0.4);
  }
  50% {
    box-shadow: 0 0 0 6px rgba(76, 175, 80, 0);
  }
}

.status-info {
  text-align: left;
}

.title {
  font-size: 18px;
  font-weight: 700;
  color: #263238;
  margin: 0 0 4px;
}

.subtitle {
  font-size: 13px;
  color: #78909c;
  margin: 0;
}

.online-status {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #4caf50;
}

.pulse-dot {
  width: 8px;
  height: 8px;
  background: #4caf50;
  border-radius: 50%;
  animation: blink 1.5s ease-in-out infinite;
}

@keyframes blink {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.4;
  }
}

.offline-status {
  color: #90a4ae;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.finish-btn {
  background: linear-gradient(135deg, #ef5350, #f44336);
  color: white;
}

.report-btn {
  background: linear-gradient(135deg, #4caf50, #66bb6a);
  color: white;
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

/* ============ 聊天内容区 ============ */
.chat-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  background: linear-gradient(180deg, #f8faf9 0%, #f4f7f6 100%);
}

.chat-content::-webkit-scrollbar {
  width: 6px;
}

.chat-content::-webkit-scrollbar-track {
  background: rgba(0, 137, 123, 0.05);
  border-radius: 3px;
}

.chat-content::-webkit-scrollbar-thumb {
  background: rgba(0, 137, 123, 0.2);
  border-radius: 3px;
}

/* 加载状态 */
.loading-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
}

.loading-animation {
  position: relative;
  width: 120px;
  height: 120px;
  margin-bottom: 30px;
}

.loading-brain {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 48px;
  z-index: 2;
  animation: brainPulse 2s ease-in-out infinite;
}

@keyframes brainPulse {
  0%,
  100% {
    transform: translate(-50%, -50%) scale(1);
  }
  50% {
    transform: translate(-50%, -50%) scale(1.1);
  }
}

.loading-rings {
  position: absolute;
  inset: 0;
}

.ring {
  position: absolute;
  inset: 0;
  border: 3px solid transparent;
  border-top-color: #00897b;
  border-radius: 50%;
  animation: ringRotate 1.5s linear infinite;
}

.ring-1 {
  animation-duration: 1.5s;
}
.ring-2 {
  inset: 10px;
  border-top-color: #26a69a;
  animation-duration: 2s;
  animation-direction: reverse;
}
.ring-3 {
  inset: 20px;
  border-top-color: #4db6ac;
  animation-duration: 2.5s;
}

@keyframes ringRotate {
  to {
    transform: rotate(360deg);
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
  color: #78909c;
  margin: 0 0 24px;
}

.loading-progress {
  width: 200px;
}

.progress-bar {
  height: 4px;
  background: rgba(0, 137, 123, 0.1);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  width: 30%;
  background: linear-gradient(90deg, #00897b, #26a69a);
  border-radius: 2px;
  animation: progressMove 1.5s ease-in-out infinite;
}

@keyframes progressMove {
  0% {
    width: 0%;
    margin-left: 0%;
  }
  50% {
    width: 50%;
    margin-left: 25%;
  }
  100% {
    width: 0%;
    margin-left: 100%;
  }
}

/* 欢迎提示 */
.welcome-tip {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px 20px;
  background: linear-gradient(135deg, rgba(0, 137, 123, 0.08), rgba(38, 166, 154, 0.05));
  border: 1px solid rgba(0, 137, 123, 0.15);
  border-radius: 14px;
  margin-bottom: 24px;
}

.tip-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.tip-content {
  font-size: 14px;
  color: #546e7a;
  line-height: 1.6;
}

.tip-content strong {
  color: #00897b;
}

/* 消息列表 */
.messages-wrapper {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.message-row {
  display: flex;
  gap: 14px;
  max-width: 85%;
  animation: messageSlide 0.4s ease-out;
}

@keyframes messageSlide {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-row.user {
  flex-direction: row-reverse;
  margin-left: auto;
}

.avatar-wrapper {
  position: relative;
  flex-shrink: 0;
}

.avatar {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  overflow: hidden;
}

.avatar.ai {
  background: linear-gradient(135deg, #00897b, #26a69a);
  box-shadow: 0 4px 15px rgba(0, 137, 123, 0.25);
}

.avatar.user {
  background: linear-gradient(135deg, #42a5f5, #1e88e5);
  box-shadow: 0 4px 15px rgba(33, 150, 243, 0.25);
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-glow {
  position: absolute;
  inset: -4px;
  border-radius: 18px;
  background: linear-gradient(135deg, rgba(0, 137, 123, 0.2), transparent);
  z-index: -1;
  opacity: 0;
  transition: opacity 0.3s;
}

.message-row:hover .avatar-glow {
  opacity: 1;
}

.message-content {
  flex: 1;
  min-width: 0;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
  padding: 0 4px;
}

.sender-name {
  font-size: 13px;
  font-weight: 600;
  color: #546e7a;
}

.message-time {
  font-size: 11px;
  color: #b0bec5;
}

.message-row.user .message-header {
  flex-direction: row-reverse;
}

.message-bubble {
  padding: 16px 20px;
  border-radius: 18px;
  position: relative;
  transition: all 0.3s;
}

.message-bubble.ai {
  background: white;
  border: 1px solid rgba(0, 137, 123, 0.1);
  border-top-left-radius: 4px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.04);
}

.message-bubble.user {
  background: linear-gradient(135deg, #00897b, #26a69a);
  color: white;
  border-top-right-radius: 4px;
  box-shadow: 0 4px 15px rgba(0, 137, 123, 0.25);
}

.message-bubble:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
}

.user-text {
  font-size: 15px;
  line-height: 1.7;
  white-space: pre-wrap;
  word-break: break-word;
}

/* Markdown 样式 */
:deep(.markdown-body) {
  font-size: 15px;
  line-height: 1.7;
  color: #37474f;
}

:deep(.markdown-body) h1,
:deep(.markdown-body) h2,
:deep(.markdown-body) h3 {
  color: #00897b;
  margin-top: 16px;
  margin-bottom: 8px;
}

:deep(.markdown-body) h3 {
  font-size: 16px;
  padding-left: 12px;
  border-left: 3px solid #00897b;
}

:deep(.markdown-body) p {
  margin: 10px 0;
}

:deep(.markdown-body) ul,
:deep(.markdown-body) ol {
  padding-left: 24px;
  margin: 10px 0;
}

:deep(.markdown-body) li {
  margin: 6px 0;
}

:deep(.markdown-body) strong {
  color: #00897b;
  font-weight: 600;
}

/* 输入中提示 */
.typing-indicator {
  display: flex;
  gap: 14px;
  max-width: 200px;
  margin-top: 16px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.typing-bubble {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  background: white;
  border: 1px solid rgba(0, 137, 123, 0.1);
  border-radius: 18px;
  border-top-left-radius: 4px;
}

.typing-dots {
  display: flex;
  gap: 4px;
}

.typing-dots span {
  width: 8px;
  height: 8px;
  background: #00897b;
  border-radius: 50%;
  animation: typingBounce 1.4s infinite;
}

.typing-dots span:nth-child(2) {
  animation-delay: 0.2s;
}
.typing-dots span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typingBounce {
  0%,
  60%,
  100% {
    transform: translateY(0);
    opacity: 0.4;
  }
  30% {
    transform: translateY(-6px);
    opacity: 1;
  }
}

.typing-text {
  font-size: 13px;
  color: #78909c;
}

.scroll-anchor {
  height: 1px;
}

/* ============ 输入区域 ============ */
.chat-footer {
  padding: 20px 24px;
  background: white;
  border-top: 1px solid rgba(0, 137, 123, 0.08);
  flex-shrink: 0;
}

.input-container {
  display: flex;
  gap: 16px;
  align-items: flex-end;
}

.input-wrapper {
  flex: 1;
  position: relative;
}

.message-input {
  width: 100%;
  padding: 14px 18px;
  padding-right: 80px;
  border: 2px solid #e8f5e9;
  border-radius: 16px;
  font-size: 15px;
  line-height: 1.6;
  resize: none;
  transition: all 0.3s;
  font-family: inherit;
}

.message-input:focus {
  outline: none;
  border-color: #00897b;
  box-shadow: 0 0 0 4px rgba(0, 137, 123, 0.1);
}

.message-input::placeholder {
  color: #b0bec5;
}

.input-tools {
  position: absolute;
  right: 16px;
  bottom: 12px;
}

.char-count {
  font-size: 12px;
  color: #b0bec5;
}

.send-btn {
  width: 56px;
  height: 56px;
  border: none;
  border-radius: 16px;
  background: #e0e0e0;
  color: #9e9e9e;
  cursor: not-allowed;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.send-btn.active {
  background: linear-gradient(135deg, #00897b, #26a69a);
  color: white;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(0, 137, 123, 0.3);
}

.send-btn.active:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 137, 123, 0.4);
}

.send-icon {
  width: 24px;
  height: 24px;
}

.send-icon svg {
  width: 100%;
  height: 100%;
}

.sending-spinner {
  width: 24px;
  height: 24px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.footer-tips {
  display: flex;
  gap: 20px;
  margin-top: 12px;
  padding-left: 4px;
}

.tip-item {
  font-size: 12px;
  color: #90a4ae;
  display: flex;
  align-items: center;
  gap: 6px;
}

kbd {
  padding: 2px 6px;
  background: #f5f5f5;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-size: 11px;
  font-family: inherit;
}

/* 对话结束状态 */
.chat-footer.ended {
  padding: 30px 24px;
}

.ended-content {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px 24px;
  background: linear-gradient(135deg, rgba(76, 175, 80, 0.1), rgba(102, 187, 106, 0.05));
  border: 1px solid rgba(76, 175, 80, 0.2);
  border-radius: 16px;
}

.ended-icon {
  font-size: 32px;
}

.ended-text {
  flex: 1;
}

.ended-text h4 {
  font-size: 16px;
  font-weight: 600;
  color: #2e7d32;
  margin: 0 0 4px;
}

.ended-text p {
  font-size: 13px;
  color: #66bb6a;
  margin: 0;
}

.view-report-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: linear-gradient(135deg, #4caf50, #66bb6a);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.view-report-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(76, 175, 80, 0.3);
}

/* ============ 确认结束弹窗 ============ */
.confirm-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 20px;
}

.confirm-modal {
  width: 100%;
  max-width: 480px;
  background: white;
  border-radius: 28px;
  box-shadow:
    0 25px 80px rgba(0, 0, 0, 0.25),
    0 0 0 1px rgba(255, 255, 255, 0.1);
  position: relative;
  overflow: hidden;
  animation: confirmAppear 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

@keyframes confirmAppear {
  from {
    opacity: 0;
    transform: scale(0.9) translateY(20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

/* 装饰背景 */
.modal-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 200px;
  overflow: hidden;
  pointer-events: none;
}

.decoration-circle {
  position: absolute;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(239, 83, 80, 0.1), rgba(244, 67, 54, 0.05));
}

.circle-1 {
  width: 200px;
  height: 200px;
  top: -100px;
  right: -50px;
}

.circle-2 {
  width: 150px;
  height: 150px;
  top: -50px;
  left: -30px;
  background: linear-gradient(135deg, rgba(255, 152, 0, 0.1), rgba(255, 193, 7, 0.05));
}

/* 弹窗头部 */
.confirm-header {
  padding: 40px 30px 24px;
  text-align: center;
  position: relative;
  z-index: 1;
}

.confirm-icon-wrapper {
  position: relative;
  width: 80px;
  height: 80px;
  margin: 0 auto 20px;
}

.confirm-icon {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #fff3e0, #ffe0b2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 1;
  box-shadow: 0 8px 25px rgba(255, 152, 0, 0.25);
}

.icon-emoji {
  font-size: 40px;
  animation: iconBounce 2s ease-in-out infinite;
}

@keyframes iconBounce {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-5px);
  }
}

.icon-ring {
  position: absolute;
  inset: -8px;
  border: 3px solid rgba(255, 152, 0, 0.2);
  border-radius: 50%;
  animation: ringPulse 2s ease-in-out infinite;
}

@keyframes ringPulse {
  0%,
  100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.5;
  }
}

.confirm-title {
  font-size: 24px;
  font-weight: 700;
  color: #263238;
  margin: 0 0 8px;
}

.confirm-subtitle {
  font-size: 14px;
  color: #78909c;
  margin: 0;
}

/* 弹窗内容 */
.confirm-body {
  padding: 0 30px 24px;
}

.info-card {
  display: flex;
  gap: 16px;
  padding: 18px 20px;
  background: linear-gradient(135deg, #f5f7fa, #e8f5e9);
  border-radius: 16px;
  margin-bottom: 20px;
}

.info-icon {
  font-size: 28px;
  flex-shrink: 0;
}

.info-content h4 {
  font-size: 15px;
  font-weight: 600;
  color: #263238;
  margin: 0 0 6px;
}

.info-content p {
  font-size: 13px;
  color: #546e7a;
  margin: 0;
  line-height: 1.6;
}

.stats-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 30px;
  padding: 20px;
  background: rgba(0, 137, 123, 0.04);
  border-radius: 14px;
  margin-bottom: 16px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.stat-icon {
  font-size: 24px;
}

.stat-value {
  font-size: 22px;
  font-weight: 700;
  color: #00897b;
}

.stat-label {
  font-size: 12px;
  color: #90a4ae;
}

.stat-divider {
  width: 1px;
  height: 50px;
  background: linear-gradient(180deg, transparent, rgba(0, 137, 123, 0.2), transparent);
}

.warning-tip {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 14px 16px;
  background: rgba(255, 152, 0, 0.08);
  border-radius: 12px;
  border-left: 4px solid #ff9800;
}

.warning-icon {
  font-size: 18px;
  flex-shrink: 0;
}

.warning-text {
  font-size: 13px;
  color: #5d4037;
  line-height: 1.5;
}

/* 弹窗底部 */
.confirm-footer {
  display: flex;
  gap: 12px;
  padding: 0 30px 30px;
}

.confirm-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 14px 24px;
  border: none;
  border-radius: 14px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.confirm-btn.cancel {
  background: #f5f5f5;
  color: #546e7a;
}

.confirm-btn.cancel:hover {
  background: #eeeeee;
  transform: translateY(-2px);
}

.confirm-btn.submit {
  background: linear-gradient(135deg, #ef5350, #f44336);
  color: white;
  box-shadow: 0 4px 15px rgba(244, 67, 54, 0.3);
}

.confirm-btn.submit:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(244, 67, 54, 0.4);
}

.confirm-btn.submit:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-loading {
  display: flex;
  align-items: center;
  gap: 10px;
}

.btn-loading .spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

/* 关闭按钮 */
.confirm-modal > .close-btn {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 36px;
  height: 36px;
  border: none;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

.confirm-modal > .close-btn svg {
  width: 18px;
  height: 18px;
  color: #78909c;
}

.confirm-modal > .close-btn:hover {
  background: rgba(244, 67, 54, 0.1);
}

.confirm-modal > .close-btn:hover svg {
  color: #f44336;
}

/* 确认弹窗动画 */
.confirm-fade-enter-active,
.confirm-fade-leave-active {
  transition: all 0.3s ease;
}

.confirm-fade-enter-from,
.confirm-fade-leave-to {
  opacity: 0;
}

.confirm-fade-enter-from .confirm-modal,
.confirm-fade-leave-to .confirm-modal {
  transform: scale(0.9) translateY(20px);
}

/* ============ 报告弹窗 ============ */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 20px;
}

.report-modal {
  width: 100%;
  max-width: 700px;
  max-height: 85vh;
  background: white;
  border-radius: 24px;
  box-shadow: 0 25px 80px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: modalAppear 0.3s ease-out;
}

@keyframes modalAppear {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #f0f0f0;
}

.modal-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 20px;
  font-weight: 700;
  color: #263238;
}

.modal-header .close-btn {
  width: 36px;
  height: 36px;
  border: none;
  background: #f5f5f5;
  border-radius: 50%;
  font-size: 24px;
  color: #78909c;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-header .close-btn:hover {
  background: #eeeeee;
  color: #f44336;
}

.modal-body {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

.report-content {
  padding: 20px;
  background: #f9fafb;
  border: 1px solid #e8f5e9;
  border-radius: 12px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid #f0f0f0;
}

.modal-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.modal-btn.secondary {
  background: #f5f5f5;
  color: #546e7a;
}

.modal-btn.secondary:hover {
  background: #eeeeee;
}

.modal-btn.primary {
  background: linear-gradient(135deg, #00897b, #26a69a);
  color: white;
}

.modal-btn.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 137, 123, 0.3);
}

/* ============ 过渡动画 ============ */
.message-fade-enter-active {
  transition: all 0.4s ease-out;
}

.message-fade-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.typing-fade-enter-active,
.typing-fade-leave-active {
  transition: all 0.3s ease;
}

.typing-fade-enter-from,
.typing-fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: all 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-fade-enter-from .report-modal,
.modal-fade-leave-to .report-modal {
  transform: scale(0.95) translateY(20px);
}

/* ============ 响应式 ============ */
@media (max-width: 768px) {
  .chat-page {
    padding: 10px;
  }

  .chat-container {
    height: 95vh;
    max-height: none;
    border-radius: 20px;
  }

  .chat-header {
    padding: 12px 16px;
    flex-wrap: wrap;
    gap: 12px;
  }

  .back-text {
    display: none;
  }

  .title {
    font-size: 16px;
  }

  .action-btn .btn-text {
    display: none;
  }

  .action-btn {
    padding: 10px 14px;
  }

  .chat-content {
    padding: 16px;
  }

  .message-row {
    max-width: 95%;
  }

  .avatar {
    width: 38px;
    height: 38px;
  }

  .message-bubble {
    padding: 12px 16px;
  }

  .chat-footer {
    padding: 16px;
  }

  .input-container {
    gap: 12px;
  }

  .send-btn {
    width: 48px;
    height: 48px;
  }

  .footer-tips {
    display: none;
  }

  /* 确认弹窗响应式 */
  .confirm-modal {
    max-width: 95%;
    border-radius: 24px;
  }

  .confirm-header {
    padding: 30px 20px 20px;
  }

  .confirm-icon-wrapper {
    width: 70px;
    height: 70px;
  }

  .icon-emoji {
    font-size: 34px;
  }

  .confirm-title {
    font-size: 20px;
  }

  .confirm-body {
    padding: 0 20px 20px;
  }

  .stats-row {
    gap: 20px;
    padding: 16px;
  }

  .stat-value {
    font-size: 20px;
  }

  .confirm-footer {
    flex-direction: column;
    padding: 0 20px 24px;
  }

  .confirm-btn {
    width: 100%;
  }

  /* 报告弹窗响应式 */
  .report-modal {
    max-height: 90vh;
    border-radius: 20px;
  }

  .modal-footer {
    flex-direction: column;
  }

  .modal-btn {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .header-center {
    order: -1;
    width: 100%;
    justify-content: center;
  }

  .ai-status {
    justify-content: center;
  }

  .status-info {
    text-align: center;
  }

  .welcome-tip {
    flex-direction: column;
    text-align: center;
  }

  .message-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 2px;
  }

  .message-row.user .message-header {
    align-items: flex-end;
  }

  .info-card {
    flex-direction: column;
    text-align: center;
  }
}
</style>
