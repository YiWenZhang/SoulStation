<template>
  <div class="report-container">
    <!-- 背景装饰 -->
    <div class="background-decoration">
      <div class="bubble bubble-1"></div>
      <div class="bubble bubble-2"></div>
      <div class="bubble bubble-3"></div>
      <div class="floating-icon icon-1">💬</div>
      <div class="floating-icon icon-2">🤖</div>
      <div class="floating-icon icon-3">💡</div>
    </div>

    <!-- 顶部导航 -->
    <header class="page-header">
      <div class="header-content">
        <div class="header-left">
          <div class="logo-section" @click="$router.push('/home')">
            <div class="logo-icon">🌸</div>
            <div class="logo-text">
              <h1 class="site-title">心灵驿站</h1>
              <p class="site-subtitle">Mental Harbor</p>
            </div>
          </div>
        </div>
        <div class="header-center">
          <h1 class="page-title">
            <span class="title-icon">🩺</span>
            AI 问诊详情报告
          </h1>
          <p class="page-subtitle">专业分析，贴心建议，守护心灵健康</p>
        </div>
        <div class="header-right">
          <div class="action-buttons">
            <button class="action-btn back-btn" @click="$router.back()">
              <span class="btn-icon">←</span>
              <span class="btn-text">返回列表</span>
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
        <h3 class="loading-title">正在加载问诊记录</h3>
        <p class="loading-subtitle">数据整理中，请稍候...</p>
      </div>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="!detail" class="error-state">
      <div class="error-content">
        <div class="error-icon">📭</div>
        <h3 class="error-title">未找到问诊记录</h3>
        <p class="error-message">该问诊记录可能已被删除或不存在</p>
        <div class="error-actions">
          <button class="error-btn primary" @click="$router.back()">返回列表</button>
          <button class="error-btn secondary" @click="$router.push('/home')">返回首页</button>
        </div>
      </div>
    </div>

    <!-- 主内容区域 -->
    <main class="main-content" v-else>
      <!-- 报告概览 -->
      <div class="report-overview">
        <div class="card overview-card">
          <div class="overview-header">
            <div class="report-meta">
              <div class="meta-item">
                <span class="meta-icon">📅</span>
                <span class="meta-label">问诊日期</span>
                <span class="meta-value">{{ detail.date }}</span>
              </div>
              <div class="meta-item">
                <span class="meta-icon">💬</span>
                <span class="meta-label">对话轮数</span>
                <span class="meta-value">{{ detail.chat_history?.length || 0 }} 轮</span>
              </div>
            </div>
            <div class="session-info">
              <div class="session-icon">🤖</div>
              <div class="session-details">
                <h3 class="session-title">AI 心理咨询师</h3>
                <p class="session-subtitle">智能分析 · 专业建议</p>
              </div>
            </div>
          </div>

          <!-- 诊断状态卡片 -->
          <div class="diagnosis-card">
            <div class="diagnosis-content">
              <div class="diagnosis-icon">
                <span>📋</span>
              </div>
              <div class="diagnosis-details">
                <h3 class="diagnosis-title">问诊已完成</h3>
                <p class="diagnosis-summary">
                  本次问诊已生成专业分析报告，包含 AI 诊断建议及完整对话回顾
                </p>
              </div>
            </div>
            <div class="diagnosis-stats">
              <div class="stat-item">
                <span class="stat-icon">👤</span>
                <span class="stat-value">{{ userMessageCount }}</span>
                <span class="stat-label">我的提问</span>
              </div>
              <div class="stat-divider"></div>
              <div class="stat-item">
                <span class="stat-icon">🤖</span>
                <span class="stat-value">{{ aiMessageCount }}</span>
                <span class="stat-label">AI 回复</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 详细内容区域 -->
      <div class="report-details">
        <!-- 左侧：AI诊断建议 -->
        <div class="report-left">
          <div class="card advice-card">
            <div class="card-header">
              <h3 class="card-title">
                <span class="title-icon">📝</span>
                AI 诊断建议
              </h3>
              <div class="card-badge">
                <span class="badge-icon">✨</span>
                <span class="badge-text">AI 生成</span>
              </div>
            </div>
            <div class="advice-content">
              <div v-if="detail.diagnosis_report" class="advice-text">
                {{ detail.diagnosis_report }}
              </div>
              <div v-else class="no-advice">
                <div class="no-advice-icon">💭</div>
                <p class="no-advice-text">本次问诊暂无总结建议</p>
              </div>
            </div>
            <div class="advice-footer">
              <div class="disclaimer">
                <span class="disclaimer-icon">⚠️</span>
                <span class="disclaimer-text">
                  本建议由 AI 生成，仅供参考，如有需要请咨询专业心理医生
                </span>
              </div>
            </div>
          </div>

          <!-- 快捷操作 -->
          <div class="card quick-actions-card">
            <div class="card-header">
              <h3 class="card-title">
                <span class="title-icon">⚡</span>
                快捷操作
              </h3>
            </div>
            <div class="actions-grid">
              <button class="quick-action-btn" @click="startNewChat">
                <span class="action-icon">💬</span>
                <span class="action-text">继续问诊</span>
              </button>
              <button class="quick-action-btn" @click="viewHistory">
                <span class="action-icon">📋</span>
                <span class="action-text">历史记录</span>
              </button>
              <button class="quick-action-btn" @click="goAssessment">
                <span class="action-icon">📊</span>
                <span class="action-text">去测评</span>
              </button>
            </div>
          </div>
        </div>

        <!-- 右侧：对话回顾 -->
        <div class="report-right">
          <div class="card chat-card">
            <div class="card-header">
              <h3 class="card-title">
                <span class="title-icon">💬</span>
                对话回顾
              </h3>
              <div class="chat-info">
                <span class="chat-count">共 {{ detail.chat_history?.length || 0 }} 条消息</span>
              </div>
            </div>

            <div class="chat-container">
              <div
                v-if="!detail.chat_history || detail.chat_history.length === 0"
                class="empty-chat"
              >
                <div class="empty-icon">💭</div>
                <p class="empty-text">暂无对话记录</p>
              </div>

              <div v-else class="chat-list">
                <TransitionGroup name="message-fade">
                  <div
                    v-for="(msg, index) in detail.chat_history"
                    :key="index"
                    class="message-wrapper"
                    :class="msg.role"
                  >
                    <div class="message-row">
                      <div class="avatar-wrapper">
                        <div class="avatar" :class="msg.role">
                          {{ msg.role === 'user' ? '👤' : '🤖' }}
                        </div>
                        <div class="avatar-glow"></div>
                      </div>

                      <div class="message-content">
                        <div class="message-header">
                          <span class="sender-name">
                            {{ msg.role === 'user' ? '我' : 'AI 咨询师' }}
                          </span>
                          <span class="message-index">#{{ index + 1 }}</span>
                        </div>
                        <div class="message-bubble">
                          <p class="bubble-text">{{ msg.content }}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </TransitionGroup>
              </div>
            </div>

            <div class="chat-footer">
              <div class="scroll-hint">
                <span class="hint-icon">↕️</span>
                <span class="hint-text">滚动查看完整对话</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getConsultationDetail, type ConsultationDetailResponse } from '@/api/history'

const route = useRoute()
const router = useRouter()
const loading = ref(true)
const detail = ref<ConsultationDetailResponse['data'] | null>(null)

// 计算属性
const userMessageCount = computed(() => {
  if (!detail.value?.chat_history) return 0
  return detail.value.chat_history.filter((m) => m.role === 'user').length
})

const aiMessageCount = computed(() => {
  if (!detail.value?.chat_history) return 0
  return detail.value.chat_history.filter((m) => m.role === 'assistant').length
})

// 获取数据
onMounted(async () => {
  const id = route.params.id as string
  if (!id) {
    router.back()
    return
  }

  try {
    const res = await getConsultationDetail(id)
    if (res.code === 200) {
      detail.value = res.data
    }
  } catch (e) {
    console.error('获取详情失败', e)
  } finally {
    loading.value = false
  }
})

// 快捷操作
const startNewChat = () => {
  router.push('/consultation/select')
}

const viewHistory = () => {
  router.push('/history')
}

const goAssessment = () => {
  router.push('/assessment?mode=scale')
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
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
}

.bubble {
  position: absolute;
  border-radius: 50%;
  background: rgba(0, 137, 123, 0.06);
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
  opacity: 0.15;
  animation: iconFloat 15s infinite ease-in-out;
}

.icon-1 {
  top: 15%;
  left: 10%;
  animation-delay: 0s;
}
.icon-2 {
  top: 60%;
  right: 8%;
  animation-delay: -5s;
}
.icon-3 {
  bottom: 20%;
  left: 15%;
  animation-delay: -10s;
}

@keyframes float {
  0%,
  100% {
    transform: translateY(0) scale(1);
  }
  50% {
    transform: translateY(-30px) scale(1.05);
  }
}

@keyframes iconFloat {
  0%,
  100% {
    transform: translateY(0) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(15deg);
  }
}

/* ============ 页面头部 ============ */
.page-header {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(0, 137, 123, 0.1);
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
  gap: 10px;
  font-weight: 700;
}

.title-icon {
  font-size: 26px;
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
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.back-btn {
  background: rgba(0, 137, 123, 0.1);
  color: #00897b;
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
}

/* ============ 主内容区域 ============ */
.main-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 30px 20px;
  position: relative;
  z-index: 1;
}

/* ============ 报告概览 ============ */
.report-overview {
  margin-bottom: 25px;
}

.card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  box-shadow: 0 10px 40px rgba(0, 137, 123, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.8);
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
  gap: 35px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.meta-icon {
  font-size: 20px;
}

.meta-label {
  color: #90a4ae;
  font-size: 13px;
}

.meta-value {
  color: #263238;
  font-size: 15px;
  font-weight: 700;
}

.session-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.session-icon {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #00897b, #26a69a);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  box-shadow: 0 6px 20px rgba(0, 137, 123, 0.3);
}

.session-title {
  color: #263238;
  font-size: 18px;
  margin: 0 0 4px;
  font-weight: 700;
}

.session-subtitle {
  color: #90a4ae;
  font-size: 12px;
  margin: 0;
}

/* 诊断状态卡片 */
.diagnosis-card {
  background: linear-gradient(135deg, rgba(0, 137, 123, 0.08), rgba(38, 166, 154, 0.05));
  border: 1px solid rgba(0, 137, 123, 0.15);
  border-radius: 16px;
  padding: 24px;
}

.diagnosis-content {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
}

.diagnosis-icon {
  width: 70px;
  height: 70px;
  background: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36px;
  box-shadow: 0 6px 20px rgba(0, 137, 123, 0.15);
}

.diagnosis-title {
  color: #00897b;
  font-size: 22px;
  margin: 0 0 8px;
  font-weight: 700;
}

.diagnosis-summary {
  color: #546e7a;
  font-size: 14px;
  margin: 0;
  line-height: 1.6;
}

.diagnosis-stats {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 40px;
  padding: 18px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 12px;
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
  font-size: 28px;
  font-weight: 700;
  color: #00897b;
}

.stat-label {
  font-size: 12px;
  color: #78909c;
}

.stat-divider {
  width: 1px;
  height: 50px;
  background: linear-gradient(180deg, transparent, rgba(0, 137, 123, 0.2), transparent);
}

/* ============ 详细内容布局 ============ */
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
  flex: 1.3;
}

/* ============ AI建议卡片 ============ */
.advice-card {
  padding: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
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

.card-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  background: linear-gradient(135deg, #e8f5e9, #e0f2f1);
  border-radius: 20px;
  font-size: 12px;
  color: #00897b;
  font-weight: 600;
}

.advice-content {
  min-height: 150px;
}

.advice-text {
  color: #455a64;
  font-size: 15px;
  line-height: 1.9;
  white-space: pre-wrap;
  text-align: justify;
  padding: 20px;
  background: rgba(0, 137, 123, 0.03);
  border-radius: 12px;
  border-left: 4px solid #00897b;
}

.no-advice {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 150px;
  color: #b0bec5;
}

.no-advice-icon {
  font-size: 48px;
  margin-bottom: 12px;
  opacity: 0.5;
}

.no-advice-text {
  margin: 0;
  font-size: 14px;
}

.advice-footer {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid rgba(0, 137, 123, 0.1);
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

/* ============ 快捷操作卡片 ============ */
.quick-actions-card {
  padding: 24px;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.quick-action-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 20px 16px;
  background: rgba(0, 137, 123, 0.05);
  border: 1px solid rgba(0, 137, 123, 0.1);
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.quick-action-btn:hover {
  background: rgba(0, 137, 123, 0.1);
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0, 137, 123, 0.15);
}

.action-icon {
  font-size: 28px;
}

.action-text {
  font-size: 13px;
  font-weight: 600;
  color: #00897b;
}

/* ============ 对话回顾卡片 ============ */
.chat-card {
  padding: 24px;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.chat-info {
  font-size: 13px;
  color: #90a4ae;
  padding: 6px 14px;
  background: rgba(0, 137, 123, 0.05);
  border-radius: 20px;
}

.chat-container {
  flex: 1;
  max-height: 500px;
  overflow-y: auto;
  padding: 10px 5px;
  margin: 0 -5px;
}

.chat-container::-webkit-scrollbar {
  width: 6px;
}

.chat-container::-webkit-scrollbar-track {
  background: rgba(0, 137, 123, 0.05);
  border-radius: 3px;
}

.chat-container::-webkit-scrollbar-thumb {
  background: rgba(0, 137, 123, 0.2);
  border-radius: 3px;
}

.chat-container::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 137, 123, 0.3);
}

.empty-chat {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #b0bec5;
}

.empty-icon {
  font-size: 56px;
  margin-bottom: 15px;
  opacity: 0.4;
}

.empty-text {
  margin: 0;
  font-size: 14px;
}

.chat-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.message-wrapper {
  animation: messageSlide 0.4s ease-out;
}

@keyframes messageSlide {
  from {
    opacity: 0;
    transform: translateY(15px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-row {
  display: flex;
  gap: 14px;
  max-width: 90%;
}

.message-wrapper.user .message-row {
  flex-direction: row-reverse;
  margin-left: auto;
}

.avatar-wrapper {
  position: relative;
  flex-shrink: 0;
}

.avatar {
  width: 42px;
  height: 42px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  position: relative;
  z-index: 1;
}

.avatar.user {
  background: linear-gradient(135deg, #00897b, #26a69a);
  box-shadow: 0 4px 15px rgba(0, 137, 123, 0.3);
}

.avatar.assistant {
  background: white;
  border: 2px solid #e0f2f1;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
}

.avatar-glow {
  position: absolute;
  inset: -3px;
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(0, 137, 123, 0.2), rgba(38, 166, 154, 0.1));
  z-index: 0;
  opacity: 0;
  transition: opacity 0.3s;
}

.message-wrapper:hover .avatar-glow {
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
}

.sender-name {
  font-size: 13px;
  font-weight: 600;
  color: #546e7a;
}

.message-index {
  font-size: 11px;
  color: #b0bec5;
  padding: 2px 8px;
  background: rgba(0, 0, 0, 0.03);
  border-radius: 10px;
}

.message-wrapper.user .message-header {
  flex-direction: row-reverse;
}

.message-bubble {
  padding: 14px 18px;
  border-radius: 16px;
  position: relative;
}

.message-wrapper.assistant .message-bubble {
  background: white;
  border: 1px solid rgba(0, 137, 123, 0.1);
  border-top-left-radius: 4px;
  box-shadow: 0 3px 12px rgba(0, 0, 0, 0.04);
}

.message-wrapper.user .message-bubble {
  background: linear-gradient(135deg, #e0f2f1, #e8f5e9);
  border-top-right-radius: 4px;
}

.bubble-text {
  margin: 0;
  font-size: 14px;
  line-height: 1.7;
  color: #37474f;
  word-wrap: break-word;
}

.chat-footer {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid rgba(0, 137, 123, 0.1);
}

.scroll-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #b0bec5;
  font-size: 12px;
}

.hint-icon {
  font-size: 14px;
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
  box-shadow: 0 25px 80px rgba(0, 137, 123, 0.15);
}

.loading-animation {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-bottom: 30px;
}

.loading-circle {
  width: 18px;
  height: 18px;
  background: linear-gradient(135deg, #00897b, #26a69a);
  border-radius: 50%;
  animation: loadingBounce 1.4s infinite ease-in-out;
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

@keyframes loadingBounce {
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
  color: #263238;
  font-size: 20px;
  margin: 0 0 10px;
  font-weight: 600;
}

.loading-subtitle {
  color: #90a4ae;
  margin: 0;
  font-size: 14px;
}

.error-icon {
  font-size: 72px;
  margin-bottom: 20px;
}

.error-title {
  color: #263238;
  font-size: 22px;
  margin: 0 0 12px;
  font-weight: 600;
}

.error-message {
  color: #78909c;
  font-size: 14px;
  margin: 0 0 30px;
  line-height: 1.6;
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
  transition: all 0.3s ease;
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
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
}

/* ============ 过渡动画 ============ */
.message-fade-enter-active {
  transition: all 0.4s ease-out;
}

.message-fade-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

/* ============ 响应式 ============ */
@media (max-width: 1200px) {
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

  .diagnosis-content {
    flex-direction: column;
    text-align: center;
  }

  .diagnosis-stats {
    flex-direction: column;
    gap: 20px;
  }

  .stat-divider {
    width: 60px;
    height: 1px;
  }

  .actions-grid {
    grid-template-columns: 1fr;
  }

  .quick-action-btn {
    flex-direction: row;
    justify-content: center;
  }

  .message-row {
    max-width: 95%;
  }
}

@media (max-width: 480px) {
  .page-header {
    padding: 12px 16px;
  }

  .main-content {
    padding: 20px 16px;
  }

  .overview-card,
  .advice-card,
  .quick-actions-card,
  .chat-card {
    padding: 20px 16px;
  }

  .page-title {
    font-size: 18px;
  }

  .btn-text {
    display: none;
  }
}
</style>
