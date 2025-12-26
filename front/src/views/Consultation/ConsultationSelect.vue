<template>
  <div class="page-container">
    <!-- 动态背景 -->
    <div class="background-decoration">
      <div class="gradient-orb orb-1"></div>
      <div class="gradient-orb orb-2"></div>
      <div class="gradient-orb orb-3"></div>
      <div class="floating-shapes">
        <div class="shape shape-1">💭</div>
        <div class="shape shape-2">🌿</div>
        <div class="shape shape-3">✨</div>
        <div class="shape shape-4">🌸</div>
        <div class="shape shape-5">💫</div>
      </div>
      <div class="grid-pattern"></div>
    </div>

    <!-- 顶部导航 -->
    <header class="page-header">
      <div class="header-content">
        <div class="header-left" @click="goHome">
          <div class="back-btn">
            <span class="back-icon">←</span>
            <span class="back-text">返回首页</span>
          </div>
        </div>
        <div class="header-title">
          <div class="title-icon">📋</div>
          <h1>选择测评报告</h1>
          <p>请选择一份历史测评报告进行AI深度问诊</p>
        </div>
        <div class="header-right">
          <div class="header-badge">
            <span class="badge-count">{{ historyList.length }}</span>
            <span class="badge-text">份报告</span>
          </div>
        </div>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="main-content">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state">
        <div class="loader">
          <div class="loader-ring"></div>
          <div class="loader-ring"></div>
          <div class="loader-ring"></div>
        </div>
        <p class="loading-text">正在加载您的测评记录...</p>
      </div>

      <!-- 列表区域 -->
      <div class="list-container" v-else-if="historyList.length > 0">
        <!-- 筛选提示 -->
        <div class="list-header">
          <div class="list-tip">
            <span class="tip-icon">💡</span>
            <span>点击选择一份报告开始深度问诊</span>
          </div>
        </div>

        <!-- 报告卡片 -->
        <TransitionGroup name="card-list" tag="div" class="cards-wrapper">
          <div
            v-for="(item, index) in historyList"
            :key="item.report_id"
            class="history-card"
            :class="{
              active: selectedId === item.report_id,
              [`risk-${item.risk_level}`]: true,
            }"
            :style="{ animationDelay: `${index * 0.1}s` }"
            @click="selectReport(item.report_id)"
          >
            <!-- 卡片装饰 -->
            <div class="card-glow"></div>
            <div class="status-bar" :class="item.risk_level">
              <div class="status-pulse"></div>
            </div>

            <!-- 卡片主体 -->
            <div class="card-body">
              <!-- 头部信息 -->
              <div class="card-header-info">
                <div class="meta-info">
                  <span class="date">
                    <span class="date-icon">📅</span>
                    {{ item.report_date }}
                  </span>
                  <span class="mode-tag">
                    <span class="mode-icon">📝</span>
                    {{ item.mode_name }}
                  </span>
                </div>
                <div class="risk-badge" :class="item.risk_level">
                  <span class="risk-dot"></span>
                  <span class="risk-text">{{ getRiskText(item.risk_level) }}</span>
                </div>
              </div>

              <!-- 摘要 -->
              <div class="card-summary">
                <h3>{{ item.summary }}</h3>
              </div>

              <!-- 问诊统计 -->
              <div class="consultation-stats">
                <div class="stat-item main-stat">
                  <div class="stat-icon">🩺</div>
                  <div class="stat-content">
                    <span class="stat-value">{{ item.consultations?.length || 0 }}</span>
                    <span class="stat-label">次问诊</span>
                  </div>
                </div>

                <div class="stat-divider"></div>

                <div class="stat-item" v-if="item.consultations && item.consultations.length > 0">
                  <div class="stat-icon">🕒</div>
                  <div class="stat-content">
                    <span class="stat-value">{{ item.consultations[0]?.date?.split(' ')[0] }}</span>
                    <span class="stat-label">最近问诊</span>
                  </div>
                </div>
                <div class="stat-item empty-stat" v-else>
                  <div class="stat-icon">✨</div>
                  <div class="stat-content">
                    <span class="stat-label">尚未问诊</span>
                  </div>
                </div>
              </div>

              <!-- 进度指示器 -->
              <div class="card-progress" v-if="item.consultations?.length">
                <div class="progress-bar">
                  <div
                    class="progress-fill"
                    :style="{ width: Math.min(item.consultations.length * 20, 100) + '%' }"
                  ></div>
                </div>
                <span class="progress-text">问诊深度</span>
              </div>
            </div>

            <!-- 选择指示器 -->
            <div class="card-selector">
              <div class="selector-ring">
                <Transition name="check">
                  <div class="selector-check" v-if="selectedId === item.report_id">
                    <svg viewBox="0 0 24 24" fill="none">
                      <path
                        d="M5 12l5 5L20 7"
                        stroke="currentColor"
                        stroke-width="3"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                      />
                    </svg>
                  </div>
                </Transition>
              </div>
              <span class="selector-text">{{
                selectedId === item.report_id ? '已选择' : '点击选择'
              }}</span>
            </div>
          </div>
        </TransitionGroup>
      </div>

      <!-- 空状态 -->
      <div v-else class="empty-state">
        <div class="empty-illustration">
          <div class="empty-circle"></div>
          <div class="empty-icon">📭</div>
          <div class="empty-sparkles">
            <span>✦</span>
            <span>✧</span>
            <span>✦</span>
          </div>
        </div>
        <h3 class="empty-title">暂无测评记录</h3>
        <p class="empty-desc">完成一次心理测评后，即可在此查看历史报告</p>
        <button class="go-test-btn" @click="goTest">
          <span class="btn-icon">🎯</span>
          <span class="btn-text">开始测评</span>
          <span class="btn-arrow">→</span>
        </button>
      </div>
    </main>

    <!-- 底部操作栏 -->
    <Transition name="footer-slide">
      <footer class="footer-action" v-if="selectedId">
        <div class="footer-glow"></div>
        <div class="footer-content">
          <div class="selected-info">
            <div class="selected-icon">✅</div>
            <div class="selected-detail">
              <span class="selected-label">已选择报告</span>
              <span class="selected-date">{{ getSelectedDate }}</span>
            </div>
          </div>
          <button class="start-btn" @click="startConsultation">
            <span class="btn-content">
              <span class="btn-icon">🤖</span>
              <span class="btn-text">开始深度问诊</span>
            </span>
            <span class="btn-arrow">
              <svg viewBox="0 0 24 24" fill="none">
                <path
                  d="M5 12h14M12 5l7 7-7 7"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>
            </span>
          </button>
        </div>
      </footer>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getHistoryList, type HistoryItem } from '../../api/history'

const router = useRouter()
const historyList = ref<HistoryItem[]>([])
const selectedId = ref<number | null>(null)
const loading = ref(true)

onMounted(async () => {
  const uid = localStorage.getItem('uid')
  if (!uid) return

  try {
    loading.value = true
    const res = await getHistoryList(uid)
    if (res.code === 200) {
      historyList.value = res.data
    }
  } catch (error) {
    console.error('获取列表失败', error)
  } finally {
    loading.value = false
  }
})

const getRiskText = (level: string) => {
  const map: Record<string, string> = {
    mild: '轻度关注',
    moderate: '中度风险',
    severe: '高风险',
    good: '状态良好',
  }
  return map[level] || '未知状态'
}

const getSelectedDate = computed(() => {
  const item = historyList.value.find((i) => i.report_id === selectedId.value)
  return item ? item.report_date : ''
})

const goHome = () => router.push('/')
const goTest = () => router.push('/assessment?mode=scale')

const selectReport = (id: number) => {
  selectedId.value = id
}

const startConsultation = () => {
  if (!selectedId.value) return
  router.push({
    name: 'consultationChat',
    params: { reportId: selectedId.value },
  })
}
</script>

<style scoped>
/* ============ 基础布局 ============ */
.page-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f0f4ff 0%, #faf0ff 50%, #f0fffc 100%);
  display: flex;
  flex-direction: column;
  padding-bottom: 100px;
  position: relative;
  overflow-x: hidden;
}

/* ============ 动态背景 ============ */
.background-decoration {
  position: fixed;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
  z-index: 0;
}

.gradient-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.5;
  animation: float 20s ease-in-out infinite;
}

.orb-1 {
  width: 400px;
  height: 400px;
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
  top: -100px;
  right: -100px;
  animation-delay: 0s;
}

.orb-2 {
  width: 300px;
  height: 300px;
  background: linear-gradient(135deg, #d299c2 0%, #fef9d7 100%);
  bottom: 20%;
  left: -100px;
  animation-delay: -7s;
}

.orb-3 {
  width: 250px;
  height: 250px;
  background: linear-gradient(135deg, #89f7fe 0%, #66a6ff 100%);
  bottom: -50px;
  right: 20%;
  animation-delay: -14s;
}

@keyframes float {
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
  opacity: 0.4;
  animation: shapeFloat 15s ease-in-out infinite;
}

.shape-1 {
  top: 15%;
  left: 10%;
  animation-delay: 0s;
}
.shape-2 {
  top: 25%;
  right: 15%;
  animation-delay: -3s;
}
.shape-3 {
  top: 50%;
  left: 5%;
  animation-delay: -6s;
}
.shape-4 {
  bottom: 30%;
  right: 10%;
  animation-delay: -9s;
}
.shape-5 {
  bottom: 15%;
  left: 20%;
  animation-delay: -12s;
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
  background-size: 40px 40px;
}

/* ============ 头部导航 ============ */
.page-header {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  padding: 16px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.5);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 900px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 20px;
}

.header-left {
  justify-self: start;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.back-btn:hover {
  background: white;
  transform: translateX(-3px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
}

.back-icon {
  font-size: 18px;
  transition: transform 0.3s;
}

.back-btn:hover .back-icon {
  transform: translateX(-3px);
}

.back-text {
  font-size: 14px;
  font-weight: 500;
  color: #546e7a;
}

.header-title {
  text-align: center;
}

.title-icon {
  font-size: 28px;
  margin-bottom: 4px;
  animation: bounce 2s ease-in-out infinite;
}

@keyframes bounce {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-5px);
  }
}

.header-title h1 {
  font-size: 20px;
  font-weight: 700;
  color: #263238;
  margin: 0;
  background: linear-gradient(135deg, #00897b, #00acc1);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-title p {
  font-size: 13px;
  color: #78909c;
  margin: 4px 0 0;
}

.header-right {
  justify-self: end;
}

.header-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: linear-gradient(135deg, #e8f5e9, #e0f7fa);
  border-radius: 20px;
  border: 1px solid rgba(0, 137, 123, 0.1);
}

.badge-count {
  font-size: 18px;
  font-weight: 700;
  color: #00897b;
}

.badge-text {
  font-size: 12px;
  color: #546e7a;
}

/* ============ 主内容区 ============ */
.main-content {
  flex: 1;
  max-width: 900px;
  margin: 0 auto;
  width: 100%;
  padding: 24px;
  position: relative;
  z-index: 1;
}

/* ============ 加载状态 ============ */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
}

.loader {
  position: relative;
  width: 80px;
  height: 80px;
}

.loader-ring {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  border: 3px solid transparent;
  border-top-color: #00897b;
  animation: spin 1.5s linear infinite;
}

.loader-ring:nth-child(2) {
  inset: 8px;
  border-top-color: #4db6ac;
  animation-duration: 2s;
  animation-direction: reverse;
}

.loader-ring:nth-child(3) {
  inset: 16px;
  border-top-color: #80cbc4;
  animation-duration: 2.5s;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-text {
  margin-top: 24px;
  color: #78909c;
  font-size: 15px;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 0.6;
  }
  50% {
    opacity: 1;
  }
}

/* ============ 列表区域 ============ */
.list-header {
  margin-bottom: 20px;
}

.list-tip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  border-radius: 25px;
  font-size: 14px;
  color: #546e7a;
  border: 1px solid rgba(0, 137, 123, 0.1);
}

.tip-icon {
  font-size: 16px;
  animation: wiggle 2s ease-in-out infinite;
}

@keyframes wiggle {
  0%,
  100% {
    transform: rotate(0deg);
  }
  25% {
    transform: rotate(-10deg);
  }
  75% {
    transform: rotate(10deg);
  }
}

/* ============ 报告卡片 ============ */
.cards-wrapper {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.history-card {
  position: relative;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 20px;
  display: flex;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  border: 2px solid rgba(255, 255, 255, 0.5);
  overflow: hidden;
  animation: cardSlideIn 0.6s ease-out backwards;
}

@keyframes cardSlideIn {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.history-card:hover {
  transform: translateY(-4px) scale(1.01);
  box-shadow:
    0 20px 40px rgba(0, 137, 123, 0.12),
    0 8px 16px rgba(0, 0, 0, 0.06);
}

.history-card.active {
  border-color: #00897b;
  background: rgba(255, 255, 255, 0.95);
  box-shadow:
    0 0 0 4px rgba(0, 137, 123, 0.1),
    0 20px 40px rgba(0, 137, 123, 0.15);
}

.card-glow {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(0, 137, 123, 0.1) 0%, transparent 70%);
  opacity: 0;
  transition: opacity 0.3s;
  pointer-events: none;
}

.history-card.active .card-glow {
  opacity: 1;
}

/* 状态条 */
.status-bar {
  width: 8px;
  flex-shrink: 0;
  position: relative;
  overflow: hidden;
}

.status-bar.mild {
  background: linear-gradient(180deg, #66bb6a, #4caf50);
}
.status-bar.moderate {
  background: linear-gradient(180deg, #ffca28, #ffb300);
}
.status-bar.severe {
  background: linear-gradient(180deg, #ef5350, #e53935);
}
.status-bar.good {
  background: linear-gradient(180deg, #26c6da, #00bcd4);
}

.status-pulse {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.4), transparent);
  animation: pulseSweep 2s ease-in-out infinite;
}

@keyframes pulseSweep {
  0%,
  100% {
    transform: translateY(-100%);
  }
  50% {
    transform: translateY(100%);
  }
}

/* 卡片主体 */
.card-body {
  flex: 1;
  padding: 20px;
}

.card-header-info {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
  flex-wrap: wrap;
  gap: 10px;
}

.meta-info {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.date,
.mode-tag {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #546e7a;
}

.date-icon,
.mode-icon {
  font-size: 14px;
}

.mode-tag {
  padding: 3px 10px;
  background: rgba(0, 137, 123, 0.08);
  border-radius: 12px;
  color: #00897b;
  font-weight: 500;
}

/* 风险标签 */
.risk-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: 15px;
  font-size: 12px;
  font-weight: 600;
}

.risk-badge.mild {
  background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
  color: #2e7d32;
}

.risk-badge.moderate {
  background: linear-gradient(135deg, #fff8e1, #ffecb3);
  color: #f57c00;
}

.risk-badge.severe {
  background: linear-gradient(135deg, #ffebee, #ffcdd2);
  color: #c62828;
}

.risk-badge.good {
  background: linear-gradient(135deg, #e0f7fa, #b2ebf2);
  color: #00838f;
}

.risk-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
  animation: blink 1.5s ease-in-out infinite;
}

@keyframes blink {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.3;
  }
}

/* 摘要 */
.card-summary {
  margin-bottom: 16px;
}

.card-summary h3 {
  font-size: 17px;
  font-weight: 600;
  color: #263238;
  margin: 0;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 问诊统计 */
.consultation-stats {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 14px 16px;
  background: linear-gradient(135deg, #f8fffe 0%, #f5f7ff 100%);
  border-radius: 14px;
  border: 1px solid rgba(0, 137, 123, 0.08);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.stat-icon {
  font-size: 20px;
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 18px;
  font-weight: 700;
  color: #00897b;
  line-height: 1.2;
}

.stat-label {
  font-size: 12px;
  color: #78909c;
}

.main-stat .stat-value {
  font-size: 24px;
}

.stat-divider {
  width: 1px;
  height: 36px;
  background: linear-gradient(180deg, transparent, rgba(0, 0, 0, 0.1), transparent);
}

.empty-stat .stat-label {
  color: #b0bec5;
  font-style: italic;
}

/* 进度条 */
.card-progress {
  margin-top: 14px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.progress-bar {
  flex: 1;
  height: 6px;
  background: #e0e0e0;
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #00897b, #26a69a, #4db6ac);
  border-radius: 3px;
  transition: width 0.6s ease;
}

.progress-text {
  font-size: 11px;
  color: #90a4ae;
  white-space: nowrap;
}

/* 选择指示器 */
.card-selector {
  width: 80px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 16px 8px;
  border-left: 1px solid rgba(0, 0, 0, 0.05);
  background: rgba(0, 137, 123, 0.02);
  transition: all 0.3s;
}

.history-card.active .card-selector {
  background: rgba(0, 137, 123, 0.08);
}

.selector-ring {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 2px solid #b0bec5;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.history-card.active .selector-ring {
  border-color: #00897b;
  background: #00897b;
}

.selector-check {
  width: 16px;
  height: 16px;
  color: white;
}

.selector-text {
  font-size: 11px;
  color: #90a4ae;
  text-align: center;
  transition: color 0.3s;
}

.history-card.active .selector-text {
  color: #00897b;
  font-weight: 600;
}

/* ============ 空状态 ============ */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60px 20px;
}

.empty-illustration {
  position: relative;
  width: 140px;
  height: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
}

.empty-circle {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  background: linear-gradient(135deg, #e0f2f1, #e8f5e9);
  animation: breathe 3s ease-in-out infinite;
}

@keyframes breathe {
  0%,
  100% {
    transform: scale(1);
    opacity: 0.8;
  }
  50% {
    transform: scale(1.08);
    opacity: 0.6;
  }
}

.empty-icon {
  font-size: 56px;
  position: relative;
  z-index: 1;
}

.empty-sparkles {
  position: absolute;
  inset: 0;
}

.empty-sparkles span {
  position: absolute;
  font-size: 16px;
  color: #00897b;
  animation: sparkle 2s ease-in-out infinite;
}

.empty-sparkles span:nth-child(1) {
  top: 10%;
  right: 15%;
  animation-delay: 0s;
}
.empty-sparkles span:nth-child(2) {
  bottom: 20%;
  left: 10%;
  animation-delay: 0.5s;
}
.empty-sparkles span:nth-child(3) {
  top: 50%;
  right: 5%;
  animation-delay: 1s;
}

@keyframes sparkle {
  0%,
  100% {
    opacity: 0;
    transform: scale(0.5);
  }
  50% {
    opacity: 1;
    transform: scale(1);
  }
}

.empty-title {
  font-size: 20px;
  font-weight: 600;
  color: #37474f;
  margin: 0 0 8px;
}

.empty-desc {
  font-size: 14px;
  color: #78909c;
  margin: 0 0 24px;
  text-align: center;
}

.go-test-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 28px;
  background: linear-gradient(135deg, #00897b, #00acc1);
  color: white;
  border: none;
  border-radius: 30px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 8px 25px rgba(0, 137, 123, 0.3);
}

.go-test-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 35px rgba(0, 137, 123, 0.4);
}

.go-test-btn .btn-arrow {
  transition: transform 0.3s;
}

.go-test-btn:hover .btn-arrow {
  transform: translateX(4px);
}

/* ============ 底部操作栏 ============ */
.footer-action {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  padding: 16px 24px;
  padding-bottom: max(16px, env(safe-area-inset-bottom));
  border-top: 1px solid rgba(255, 255, 255, 0.5);
  z-index: 100;
}

.footer-glow {
  position: absolute;
  top: -30px;
  left: 50%;
  transform: translateX(-50%);
  width: 200px;
  height: 60px;
  background: radial-gradient(ellipse, rgba(0, 137, 123, 0.15) 0%, transparent 70%);
  pointer-events: none;
}

.footer-content {
  max-width: 900px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.selected-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.selected-icon {
  font-size: 24px;
  animation: pop 0.4s ease-out;
}

@keyframes pop {
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

.selected-detail {
  display: flex;
  flex-direction: column;
}

.selected-label {
  font-size: 12px;
  color: #78909c;
}

.selected-date {
  font-size: 15px;
  font-weight: 600;
  color: #00897b;
}

.start-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 24px;
  background: linear-gradient(135deg, #00897b, #00796b);
  color: white;
  border: none;
  border-radius: 30px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 6px 20px rgba(0, 137, 123, 0.35);
  overflow: hidden;
  position: relative;
}

.start-btn::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.2), transparent);
  opacity: 0;
  transition: opacity 0.3s;
}

.start-btn:hover::before {
  opacity: 1;
}

.start-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(0, 137, 123, 0.45);
}

.start-btn .btn-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.start-btn .btn-arrow {
  width: 20px;
  height: 20px;
  transition: transform 0.3s;
}

.start-btn:hover .btn-arrow {
  transform: translateX(4px);
}

/* ============ 过渡动画 ============ */
.card-list-enter-active,
.card-list-leave-active {
  transition: all 0.4s ease;
}

.card-list-enter-from {
  opacity: 0;
  transform: translateY(30px);
}

.card-list-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}

.check-enter-active,
.check-leave-active {
  transition: all 0.3s ease;
}

.check-enter-from,
.check-leave-to {
  opacity: 0;
  transform: scale(0);
}

.footer-slide-enter-active,
.footer-slide-leave-active {
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.footer-slide-enter-from,
.footer-slide-leave-to {
  transform: translateY(100%);
  opacity: 0;
}

/* ============ 响应式 ============ */
@media (max-width: 640px) {
  .header-content {
    grid-template-columns: auto 1fr auto;
    gap: 12px;
  }

  .back-text {
    display: none;
  }

  .header-title h1 {
    font-size: 18px;
  }
  .header-title p {
    font-size: 12px;
  }

  .title-icon {
    font-size: 24px;
  }

  .header-badge {
    padding: 6px 12px;
  }
  .badge-count {
    font-size: 16px;
  }

  .main-content {
    padding: 16px;
  }

  .card-body {
    padding: 16px;
  }

  .card-summary h3 {
    font-size: 15px;
  }

  .consultation-stats {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .stat-divider {
    display: none;
  }

  .card-selector {
    width: 60px;
    padding: 12px 6px;
  }

  .footer-content {
    flex-direction: column;
    gap: 12px;
  }

  .start-btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
