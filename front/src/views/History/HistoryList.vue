<template>
  <div class="history-container">
    <!-- 背景装饰 -->
    <div class="background-decoration">
      <div class="bubble bubble-1"></div>
      <div class="bubble bubble-2"></div>
      <div class="bubble bubble-3"></div>
      <div class="floating-icon icon-1">📋</div>
      <div class="floating-icon icon-2">💬</div>
      <div class="floating-icon icon-3">📊</div>
    </div>

    <!-- 页面头部 -->
    <header class="page-header">
      <div class="header-content">
        <div class="header-left">
          <button class="back-btn" @click="$router.push('/home')">
            <span class="back-icon">←</span>
            <span class="back-text">返回首页</span>
          </button>
        </div>
        <div class="header-center">
          <h1 class="page-title">
            <span class="title-icon">📚</span>
            历史测评档案
          </h1>
          <p class="page-subtitle">查看您的心理健康测评历程</p>
        </div>
        <div class="header-right">
          <div class="stats-badge" v-if="list.length > 0">
            <span class="stats-count">{{ list.length }}</span>
            <span class="stats-label">份报告</span>
          </div>
        </div>
      </div>
    </header>

    <!-- 主内容区域 -->
    <main class="history-content">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state">
        <div class="loading-animation">
          <div class="loading-circle"></div>
          <div class="loading-circle"></div>
          <div class="loading-circle"></div>
        </div>
        <p class="loading-text">正在加载您的档案...</p>
      </div>

      <!-- 空状态 -->
      <div v-else-if="list.length === 0" class="empty-state">
        <div class="empty-illustration">
          <div class="empty-circle"></div>
          <div class="empty-icon">📭</div>
        </div>
        <h3 class="empty-title">暂无测评记录</h3>
        <p class="empty-desc">完成一次心理测评，开启您的心灵健康之旅</p>
        <button class="start-btn" @click="$router.push('/assessment')">
          <span class="btn-icon">🎯</span>
          <span>开始第一次测评</span>
        </button>
      </div>

      <!-- 记录列表 -->
      <div v-else class="record-list">
        <TransitionGroup name="card-list">
          <div
            v-for="(item, index) in list"
            :key="item.report_id"
            class="record-card"
            :style="{ animationDelay: `${index * 0.1}s` }"
          >
            <!-- 卡片主体 -->
            <div class="card-main" @click="toggleExpand(item.report_id)">
              <div class="main-left">
                <div class="date-badge" :class="item.risk_level">
                  <span class="day">{{ formatDateDay(item.report_date) }}</span>
                  <span class="month">{{ formatDateMonth(item.report_date) }}</span>
                </div>
                <div class="info-group">
                  <div class="report-title">
                    {{ item.mode_name }}
                    <span class="risk-tag" :class="item.risk_level">
                      {{ getRiskLabel(item.risk_level) }}
                    </span>
                  </div>
                  <div class="report-summary">{{ item.summary }}</div>
                  <div class="report-meta">
                    <span class="meta-item">
                      <span class="meta-icon">🩺</span>
                      {{ item.consultations?.length || 0 }} 次问诊
                    </span>
                  </div>
                </div>
              </div>

              <div class="main-right">
                <div class="score-display" v-if="item.total_score > 0">
                  <span class="score-label">总分</span>
                  <span class="score-value">{{ item.total_score }}</span>
                </div>
                <div
                  class="expand-icon"
                  :class="{ 'is-expanded': expandedIds.has(item.report_id) }"
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M6 9l6 6 6-6" />
                  </svg>
                </div>
              </div>
            </div>

            <!-- 快捷操作按钮 -->
            <div class="quick-actions">
              <button class="quick-btn view-report" @click.stop="viewReport(item.report_id)">
                <span class="btn-icon">📊</span>
                <span>查看测评报告</span>
              </button>
              <button
                class="quick-btn new-consult"
                @click.stop="gotoNewConsultation(item.report_id)"
              >
                <span class="btn-icon">💬</span>
                <span>开始问诊</span>
              </button>
            </div>

            <!-- 展开的问诊列表 -->
            <Transition name="expand">
              <div v-if="expandedIds.has(item.report_id)" class="consultation-section">
                <div class="section-header">
                  <span class="section-icon">🤖</span>
                  <span class="section-title">AI 问诊记录</span>
                  <span class="section-count">{{ item.consultations?.length || 0 }} 次</span>
                </div>

                <!-- 无问诊记录 -->
                <div
                  v-if="!item.consultations || item.consultations.length === 0"
                  class="no-consultation"
                >
                  <div class="no-data-icon">💭</div>
                  <p class="no-data-text">暂无问诊记录</p>
                  <p class="no-data-hint">基于此测评报告开始 AI 问诊，获取更深入的分析建议</p>
                  <button
                    class="add-consultation-btn"
                    @click.stop="gotoNewConsultation(item.report_id)"
                  >
                    <span class="btn-icon">+</span>
                    <span>发起问诊</span>
                  </button>
                </div>

                <!-- 问诊列表 -->
                <div v-else class="consultation-list">
                  <div
                    v-for="cons in item.consultations"
                    :key="cons.id"
                    class="consultation-item"
                    @click.stop="viewConsultation(item.report_id, cons.id)"
                  >
                    <div class="cons-left">
                      <div class="sequence-badge">
                        <span class="seq-icon">💬</span>
                        <span class="seq-text">第 {{ cons.sequence_number }} 次</span>
                      </div>
                      <div class="cons-time">{{ cons.date }}</div>
                    </div>
                    <div class="cons-center">
                      <!-- 👇 修改：显示固定文本，根据是否为第一次问诊显示不同内容 -->
                      <div class="cons-title">
                        {{ getConsultationTitle(cons.sequence_number) }}
                      </div>
                    </div>
                    <div class="cons-right">
                      <span class="status-tag" :class="cons.status">
                        {{ cons.status === 'completed' ? '✓ 已完成' : '● 进行中' }}
                      </span>
                      <span class="arrow-icon">→</span>
                    </div>
                  </div>
                </div>
              </div>
            </Transition>
          </div>
        </TransitionGroup>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getHistoryList, type HistoryItem } from '@/api/history'

const router = useRouter()
const list = ref<HistoryItem[]>([])
const loading = ref(true)
const expandedIds = ref<Set<number>>(new Set())

// 日期格式化
const formatDateDay = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.getDate().toString().padStart(2, '0')
}

const formatDateMonth = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.getMonth() + 1 + '月'
}

// 风险等级标签
const getRiskLabel = (level: string) => {
  const map: Record<string, string> = {
    mild: '轻度风险',
    moderate: '中度风险',
    severe: '重点关注',
    normal: '状态良好',
    good: '状态良好',
  }
  return map[level] || level
}

// 获取问诊记录标题
const getConsultationTitle = (sequenceNumber: number): string => {
  return sequenceNumber === 1 ? '心理咨询病历' : '心理咨询病历（复诊）'
}

// 展开/收起
const toggleExpand = (id: number) => {
  if (expandedIds.value.has(id)) {
    expandedIds.value.delete(id)
  } else {
    expandedIds.value.add(id)
  }
}

// 查看测评报告（不带问诊记录）
const viewReport = (reportId: number) => {
  router.push({
    name: 'combinedReport',
    params: { reportId },
  })
}

// 查看测评报告 + 问诊记录
const viewConsultation = (reportId: number, consultationId: number) => {
  router.push({
    name: 'combinedReport',
    params: { reportId },
    query: { consultationId: consultationId.toString() },
  })
}

// 发起新问诊（跳转到问诊聊天页）
const gotoNewConsultation = (reportId: number) => {
  router.push({
    name: 'consultationChat',
    params: { reportId },
  })
}

// 获取数据
onMounted(async () => {
  const uid = localStorage.getItem('uid')
  if (!uid) {
    router.push('/login')
    return
  }

  try {
    const res = await getHistoryList(uid)
    if (res.code === 200) {
      list.value = res.data
      // 默认展开最新的一个
      if (list.value.length > 0) {
        expandedIds.value.add(list.value[0]!.report_id)
      }
    }
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
/* ============ 基础布局 ============ */
.history-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8f9ff 0%, #f0f7ff 50%, #e8f5e9 100%);
  position: relative;
  padding-bottom: 40px;
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
  width: 300px;
  height: 300px;
  top: -80px;
  right: -60px;
}
.bubble-2 {
  width: 200px;
  height: 200px;
  bottom: 15%;
  left: -50px;
  animation-delay: -7s;
}
.bubble-3 {
  width: 150px;
  height: 150px;
  top: 50%;
  right: 10%;
  animation-delay: -14s;
}

.floating-icon {
  position: absolute;
  font-size: 24px;
  opacity: 0.12;
  animation: iconFloat 18s infinite ease-in-out;
}

.icon-1 {
  top: 15%;
  left: 8%;
}
.icon-2 {
  top: 45%;
  right: 5%;
  animation-delay: -6s;
}
.icon-3 {
  bottom: 25%;
  left: 15%;
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
    transform: translateY(-15px) rotate(8deg);
  }
}

/* ============ 页面头部 ============ */
.page-header {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(0, 137, 123, 0.08);
  padding: 16px 24px;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 900px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.header-center {
  text-align: center;
}

.page-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  font-size: 22px;
  font-weight: 700;
  color: #263238;
  margin: 0;
}

.title-icon {
  font-size: 26px;
}

.page-subtitle {
  color: #90a4ae;
  font-size: 13px;
  margin: 6px 0 0;
}

.stats-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: linear-gradient(135deg, #e8f5e9, #e0f7fa);
  border-radius: 20px;
}

.stats-count {
  font-size: 20px;
  font-weight: 700;
  color: #00897b;
}

.stats-label {
  font-size: 13px;
  color: #546e7a;
}

/* ============ 主内容区域 ============ */
.history-content {
  max-width: 900px;
  margin: 0 auto;
  padding: 24px 20px;
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

.loading-animation {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
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

.loading-text {
  color: #78909c;
  font-size: 15px;
  margin: 0;
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
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 56px;
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
}

.start-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 28px;
  background: linear-gradient(135deg, #00897b, #26a69a);
  color: white;
  border: none;
  border-radius: 14px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 6px 20px rgba(0, 137, 123, 0.3);
}

.start-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(0, 137, 123, 0.4);
}

/* ============ 记录卡片 ============ */
.record-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.record-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 137, 123, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.8);
  overflow: hidden;
  transition: all 0.3s ease;
  animation: cardSlideIn 0.5s ease-out backwards;
}

@keyframes cardSlideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.record-card:hover {
  box-shadow: 0 12px 40px rgba(0, 137, 123, 0.12);
}

.card-main {
  padding: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  transition: background 0.3s;
}

.card-main:hover {
  background: rgba(0, 137, 123, 0.02);
}

.main-left {
  display: flex;
  gap: 18px;
  align-items: flex-start;
  flex: 1;
}

/* 日期徽章 */
.date-badge {
  background: linear-gradient(135deg, #e0f2f1, #e8f5e9);
  border-radius: 14px;
  padding: 12px 16px;
  text-align: center;
  min-width: 70px;
  border: 1px solid rgba(0, 137, 123, 0.1);
}

.date-badge.severe {
  background: linear-gradient(135deg, #ffebee, #fce4ec);
  border-color: rgba(244, 67, 54, 0.1);
}

.date-badge.moderate {
  background: linear-gradient(135deg, #fff8e1, #fff3e0);
  border-color: rgba(255, 152, 0, 0.1);
}

.day {
  display: block;
  font-size: 24px;
  font-weight: 700;
  color: #00897b;
  line-height: 1;
}

.date-badge.severe .day {
  color: #e53935;
}
.date-badge.moderate .day {
  color: #f57c00;
}

.month {
  display: block;
  font-size: 12px;
  color: #78909c;
  margin-top: 4px;
}

/* 信息组 */
.info-group {
  flex: 1;
}

.report-title {
  font-size: 18px;
  font-weight: 700;
  color: #263238;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.risk-tag {
  font-size: 11px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 12px;
  color: white;
}

.risk-tag.mild,
.risk-tag.normal,
.risk-tag.good {
  background: linear-gradient(135deg, #4caf50, #66bb6a);
}

.risk-tag.moderate {
  background: linear-gradient(135deg, #ff9800, #ffb74d);
}

.risk-tag.severe {
  background: linear-gradient(135deg, #f44336, #ef5350);
}

.report-summary {
  color: #546e7a;
  font-size: 14px;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-bottom: 10px;
}

.report-meta {
  display: flex;
  gap: 16px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #78909c;
}

.meta-icon {
  font-size: 14px;
}

/* 右侧区域 */
.main-right {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-left: 20px;
}

.score-display {
  text-align: center;
  padding: 10px 16px;
  background: rgba(0, 137, 123, 0.05);
  border-radius: 12px;
}

.score-label {
  display: block;
  font-size: 11px;
  color: #90a4ae;
  margin-bottom: 2px;
}

.score-value {
  font-size: 28px;
  font-weight: 700;
  color: #00897b;
}

.expand-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #b0bec5;
  transition: all 0.3s;
}

.expand-icon svg {
  width: 20px;
  height: 20px;
}

.expand-icon.is-expanded {
  transform: rotate(180deg);
  color: #00897b;
}

/* ============ 快捷操作按钮 ============ */
.quick-actions {
  display: flex;
  gap: 12px;
  padding: 0 24px 20px;
}

.quick-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  border: none;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.quick-btn.view-report {
  background: linear-gradient(135deg, #00897b, #26a69a);
  color: white;
}

.quick-btn.new-consult {
  background: rgba(0, 137, 123, 0.1);
  color: #00897b;
}

.quick-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.quick-btn .btn-icon {
  font-size: 16px;
}

/* ============ 问诊列表区域 ============ */
.consultation-section {
  background: rgba(0, 137, 123, 0.02);
  border-top: 1px solid rgba(0, 137, 123, 0.08);
  padding: 20px 24px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px dashed rgba(0, 137, 123, 0.15);
}

.section-icon {
  font-size: 20px;
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  color: #37474f;
}

.section-count {
  font-size: 12px;
  color: #90a4ae;
  padding: 3px 10px;
  background: rgba(0, 137, 123, 0.08);
  border-radius: 12px;
  margin-left: auto;
}

/* 无问诊记录 */
.no-consultation {
  text-align: center;
  padding: 30px 20px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 14px;
  border: 1px dashed rgba(0, 137, 123, 0.2);
}

.no-data-icon {
  font-size: 40px;
  margin-bottom: 12px;
  opacity: 0.6;
}

.no-data-text {
  font-size: 15px;
  color: #546e7a;
  margin: 0 0 6px;
}

.no-data-hint {
  font-size: 13px;
  color: #90a4ae;
  margin: 0 0 16px;
}

.add-consultation-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 22px;
  background: white;
  border: 2px solid #00897b;
  color: #00897b;
  border-radius: 25px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.add-consultation-btn:hover {
  background: #00897b;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 137, 123, 0.25);
}

/* 问诊列表 */
.consultation-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.consultation-item {
  display: flex;
  align-items: center;
  padding: 16px 18px;
  background: white;
  border-radius: 14px;
  border: 1px solid rgba(0, 137, 123, 0.1);
  cursor: pointer;
  transition: all 0.3s;
}

.consultation-item:hover {
  border-color: #00897b;
  transform: translateX(6px);
  box-shadow: 0 4px 16px rgba(0, 137, 123, 0.12);
}

.cons-left {
  min-width: 130px;
}

.sequence-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #00897b;
  font-weight: 600;
  font-size: 14px;
}

.seq-icon {
  font-size: 16px;
}

.cons-time {
  color: #90a4ae;
  font-size: 12px;
  margin-top: 4px;
  margin-left: 22px;
}

.cons-center {
  flex: 1;
  padding: 0 20px;
  min-height: 50px;
  display: flex;
  align-items: center;
}

/* 问诊标题样式 */
.cons-title {
  color: #263238;
  font-size: 16px;
  font-weight: 600;
  line-height: 1.4;
}

.cons-summary {
  color: #546e7a;
  font-size: 14px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.cons-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-tag {
  font-size: 12px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 10px;
}

.status-tag.completed {
  background: #e8f5e9;
  color: #43a047;
}

.status-tag.ongoing {
  background: #fff3e0;
  color: #fb8c00;
}

.arrow-icon {
  color: #b0bec5;
  font-size: 18px;
  transition:
    transform 0.3s,
    color 0.3s;
}

.consultation-item:hover .arrow-icon {
  transform: translateX(4px);
  color: #00897b;
}

/* ============ 展开动画 ============ */
.expand-enter-active,
.expand-leave-active {
  transition: all 0.4s ease;
  max-height: 500px;
  opacity: 1;
  overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
  max-height: 0;
  opacity: 0;
  padding-top: 0;
  padding-bottom: 0;
}

/* ============ 列表动画 ============ */
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

/* ============ 响应式 ============ */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 15px;
  }

  .back-text {
    display: none;
  }

  .card-main {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .main-left {
    flex-direction: column;
    width: 100%;
  }

  .date-badge {
    flex-direction: row;
    gap: 8px;
    width: fit-content;
  }

  .day,
  .month {
    display: inline;
  }

  .main-right {
    margin-left: 0;
    width: 100%;
    justify-content: space-between;
  }

  .quick-actions {
    flex-direction: column;
  }

  .quick-btn {
    justify-content: center;
  }

  .consultation-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .cons-center {
    padding: 0;
    width: 100%;
    min-height: auto;
  }

  .cons-right {
    width: 100%;
    justify-content: space-between;
  }

  /* 移动端问诊标题优化 */
  .cons-title {
    font-size: 15px;
  }
}

@media (max-width: 480px) {
  .page-header {
    padding: 12px 16px;
  }

  .history-content {
    padding: 16px;
  }

  .page-title {
    font-size: 18px;
  }

  .record-card {
    border-radius: 16px;
  }

  .card-main {
    padding: 18px;
  }

  .quick-actions {
    padding: 0 18px 18px;
  }

  .consultation-section {
    padding: 16px 18px;
  }

  .cons-title {
    font-size: 14px;
  }
}
</style>
