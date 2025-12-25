<template>
  <div class="history-container">
    <div class="page-header">
      <button class="back-btn" @click="$router.push('/home')">← 返回首页</button>
      <h1 class="page-title">历史测评档案</h1>
      <div class="placeholder"></div>
    </div>

    <div class="history-content">
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>正在加载您的档案...</p>
      </div>

      <div v-else-if="list.length === 0" class="empty-state">
        <div class="empty-icon">📭</div>
        <p>暂无测评记录</p>
        <button class="start-btn" @click="$router.push('/assessment')">开始第一次测评</button>
      </div>

      <div v-else class="record-list">
        <div v-for="item in list" :key="item.report_id" class="record-card">
          <div class="card-main" @click="toggleExpand(item.report_id)">
            <div class="main-left">
              <div class="date-badge">
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
              </div>
            </div>

            <div class="main-right">
              <div class="score-display" v-if="item.total_score > 0">
                <span class="score-label">总分</span>
                <span class="score-value">{{ item.total_score }}</span>
              </div>
              <div class="expand-icon" :class="{ 'is-expanded': expandedIds.has(item.report_id) }">
                ▼
              </div>
            </div>
          </div>

          <transition name="expand">
            <div v-if="expandedIds.has(item.report_id)" class="consultation-section">
              <div class="section-divider">
                <span class="divider-text"
                  >关联的 AI 问诊记录 ({{ item.consultations.length }})</span
                >
              </div>

              <div v-if="item.consultations.length === 0" class="no-consultation">
                <p>暂无后续问诊记录</p>
                <button class="add-consultation-btn" @click="gotoNewConsultation">
                  + 发起问诊
                </button>
              </div>

              <div class="consultation-list">
                <div
                  v-for="cons in item.consultations"
                  :key="cons.id"
                  class="consultation-item"
                  @click.stop="viewConsultation(cons.id)"
                >
                  <div class="cons-left">
                    <div class="sequence-badge">第 {{ cons.sequence_number }} 次问诊</div>
                    <div class="cons-time">{{ cons.date }}</div>
                  </div>
                  <div class="cons-center">
                    <div class="cons-summary">{{ cons.summary_snippet }}</div>
                  </div>
                  <div class="cons-right">
                    <span class="status-text" :class="cons.status">
                      {{ cons.status === 'completed' ? '已完成' : '进行中' }}
                    </span>
                    <span class="arrow">→</span>
                  </div>
                </div>
              </div>
            </div>
          </transition>
        </div>
      </div>
    </div>
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

const formatDateDay = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.getDate().toString().padStart(2, '0')
}

const formatDateMonth = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.getMonth() + 1 + '月'
}

const getRiskLabel = (level: string) => {
  const map: Record<string, string> = {
    mild: '轻度风险',
    moderate: '中度风险',
    severe: '重点关注',
    normal: '状态良好',
  }
  return map[level] || level
}

const toggleExpand = (id: number) => {
  if (expandedIds.value.has(id)) {
    expandedIds.value.delete(id)
  } else {
    expandedIds.value.add(id)
  }
}

const viewConsultation = (id: number) => {
  router.push(`/history/consultation/${id}`)
}

const gotoNewConsultation = () => {
  router.push('/consultation/select')
}

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
.history-container {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 800px;
  margin: 0 auto 30px;
}

.back-btn {
  background: none;
  border: none;
  color: #666;
  cursor: pointer;
  font-size: 16px;
  padding: 10px;
}

.page-title {
  color: #2c3e50;
  font-size: 20px;
  font-weight: 700;
}

.placeholder {
  width: 80px;
}

.history-content {
  max-width: 800px;
  margin: 0 auto;
}

/* 列表卡片样式 */
.record-card {
  background: white;
  border-radius: 16px;
  margin-bottom: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  transition: all 0.3s ease;
}

.card-main {
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
}

.card-main:hover {
  background: #fafafa;
}

.main-left {
  display: flex;
  gap: 15px;
  align-items: flex-start;
  flex: 1;
}

.date-badge {
  background: #e0f2f1;
  color: #00897b;
  border-radius: 12px;
  padding: 8px 12px;
  text-align: center;
  display: flex;
  flex-direction: column;
  min-width: 60px;
}

.day {
  font-size: 20px;
  font-weight: 700;
  line-height: 1;
}
.month {
  font-size: 12px;
  margin-top: 2px;
}

.info-group {
  flex: 1;
}

.report-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 6px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.risk-tag {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
  color: white;
}
.risk-tag.mild {
  background: #4caf50;
}
.risk-tag.moderate {
  background: #ff9800;
}
.risk-tag.severe {
  background: #f44336;
}
.risk-tag.normal {
  background: #2196f3;
}

.report-summary {
  color: #666;
  font-size: 14px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.main-right {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-left: 20px;
}

.score-display {
  text-align: right;
}
.score-label {
  display: block;
  font-size: 12px;
  color: #999;
}
.score-value {
  font-size: 24px;
  font-weight: 700;
  color: #00897b;
}

.expand-icon {
  color: #ccc;
  transition: transform 0.3s;
}
.expand-icon.is-expanded {
  transform: rotate(180deg);
}

/* 展开后的问诊列表区域 */
.consultation-section {
  background: #fcfcfc;
  border-top: 1px solid #eee;
  padding: 0 20px 20px;
}

.section-divider {
  padding: 15px 0 10px;
  color: #999;
  font-size: 12px;
  border-bottom: 1px dashed #eee;
  margin-bottom: 10px;
}

.no-consultation {
  text-align: center;
  padding: 20px;
  color: #999;
  font-size: 14px;
}

.add-consultation-btn {
  margin-top: 10px;
  padding: 6px 16px;
  background: white;
  border: 1px solid #00897b;
  color: #00897b;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.2s;
}

.add-consultation-btn:hover {
  background: #e0f2f1;
}

.consultation-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: white;
  border-radius: 8px;
  margin-bottom: 10px;
  border: 1px solid #eee;
  cursor: pointer;
  transition: all 0.2s;
}

.consultation-item:hover {
  border-color: #b2dfdb;
  transform: translateX(5px);
}

.cons-left {
  width: 120px;
}
.sequence-badge {
  color: #00897b;
  font-weight: 600;
  font-size: 14px;
}
.cons-time {
  color: #999;
  font-size: 12px;
  margin-top: 4px;
}

.cons-center {
  flex: 1;
  padding: 0 15px;
}
.cons-summary {
  color: #555;
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 300px;
}

.cons-right {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #ccc;
}
.status-text {
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 4px;
}
.status-text.completed {
  background: #e8f5e9;
  color: #43a047;
}
.status-text.ongoing {
  background: #fff3e0;
  color: #fb8c00;
}

/* 动画 */
.expand-enter-active,
.expand-leave-active {
  transition: all 0.3s ease;
  max-height: 500px;
  opacity: 1;
}
.expand-enter-from,
.expand-leave-to {
  max-height: 0;
  opacity: 0;
}
</style>
