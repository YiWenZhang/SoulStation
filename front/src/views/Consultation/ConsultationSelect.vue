<template>
  <div class="page-container">
    <div class="background-decoration">
      <div class="bubble bubble-1"></div>
      <div class="bubble bubble-2"></div>
    </div>

    <header class="page-header">
      <div class="header-content">
        <div class="header-left" @click="goHome">
          <div class="logo-icon">🌸</div>
          <span class="logo-text">返回首页</span>
        </div>
        <div class="header-title">
          <h1>选择测评报告</h1>
          <p>请选择一份历史测评报告进行AI深度问诊</p>
        </div>
        <div class="header-right"></div>
      </div>
    </header>

    <main class="main-content">
      <div v-if="loading" class="loading-state">加载中...</div>

      <div class="list-container" v-else-if="historyList.length > 0">
        <div
          v-for="item in historyList"
          :key="item.report_id"
          class="history-card"
          :class="{ active: selectedId === item.report_id }"
          @click="selectReport(item.report_id)"
        >
          <div class="status-bar" :class="item.risk_level"></div>

          <div class="card-body">
            <div class="card-header-info">
              <div class="meta-info">
                <span class="date">📅 {{ item.report_date }}</span>
                <span class="mode-tag">{{ item.mode_name }}</span>
              </div>
              <div class="risk-tag" :class="item.risk_level">
                {{ getRiskText(item.risk_level) }}
              </div>
            </div>

            <div class="card-summary">
              <h3>{{ item.summary }}</h3>
            </div>

            <div class="consultation-info">
              <div class="info-item">
                <span class="icon">🩺</span>
                <span class="label">AI问诊记录:</span>
                <span class="value highlight">{{ item.consultations?.length || 0 }} 次</span>
              </div>

              <div class="info-item" v-if="item.consultations && item.consultations.length > 0">
                <span class="icon">🕒</span>
                <span class="label">最近:</span>
                <span class="value">{{ item.consultations[0]?.date?.split(' ')[0] }}</span>
              </div>
              <div class="info-item" v-else>
                <span class="icon">✨</span>
                <span class="value text-gray">尚未进行过问诊</span>
              </div>
            </div>
          </div>

          <div class="card-action">
            <div class="radio-indicator">
              <div class="radio-inner" v-if="selectedId === item.report_id"></div>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="empty-state">
        <div class="empty-icon">📭</div>
        <p>暂无历史测评记录</p>
        <button class="go-test-btn" @click="goTest">去测评</button>
      </div>
    </main>

    <footer class="footer-action" :class="{ visible: !!selectedId }">
      <div class="footer-content">
        <div class="selected-tip">
          已选择报告：<span>{{ getSelectedDate }}</span>
        </div>
        <button class="start-btn" @click="startConsultation" :disabled="!selectedId">
          开始深度问诊
          <span class="arrow">→</span>
        </button>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getHistoryList, type HistoryItem } from '../../api/history' // 使用我们新建的 api/history.ts

const router = useRouter()
const historyList = ref<HistoryItem[]>([])
const selectedId = ref<number | null>(null)
const loading = ref(true)

// 获取数据
onMounted(async () => {
  const uid = localStorage.getItem('uid')
  if (!uid) return

  try {
    loading.value = true
    // 调用真实接口
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

// 辅助函数
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

// 交互方法
const goHome = () => router.push('/')
const goTest = () => router.push('/assessment?mode=scale')

const selectReport = (id: number) => {
  selectedId.value = id
}

const startConsultation = () => {
  if (!selectedId.value) return

  console.log('开始问诊，选中的报告ID:', selectedId.value)
  // 跳转到聊天界面 (确保你有这个路由，后续我们会写)
  // 这里的逻辑是：带着 report_id 去创建一个新的对话 Session
  router.push(`/consultation/chat?report_id=${selectedId.value}`)
}
</script>

<style scoped>
/* 样式保持大部分不变，微调了一些配色 */
.page-container {
  min-height: 100vh;
  background: #f8f9ff;
  display: flex;
  flex-direction: column;
  padding-bottom: 80px;
}

.page-header {
  background: white;
  padding: 15px 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
  color: #546e7a;
  font-weight: 600;
  font-size: 14px;
}

.header-title {
  text-align: center;
}
.header-title h1 {
  font-size: 18px;
  color: #263238;
  margin: 0;
}
.header-title p {
  font-size: 12px;
  color: #90a4ae;
  margin: 2px 0 0;
}

.main-content {
  flex: 1;
  max-width: 800px;
  margin: 20px auto;
  width: 100%;
  padding: 0 20px;
}

.loading-state {
  text-align: center;
  padding: 40px;
  color: #999;
}

.history-card {
  background: white;
  border-radius: 12px;
  margin-bottom: 15px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 137, 123, 0.05);
  display: flex;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 2px solid transparent;
}

.history-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 137, 123, 0.1);
}
.history-card.active {
  border-color: #00897b;
  background: #f0fdfc;
}

.status-bar {
  width: 6px;
  flex-shrink: 0;
}
.status-bar.mild {
  background: #4caf50;
}
.status-bar.moderate {
  background: #ffb300;
}
.status-bar.severe {
  background: #e53935;
}
.status-bar.good {
  background: #00bcd4;
}

.card-body {
  flex: 1;
  padding: 15px;
}

.card-header-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}
.meta-info {
  font-size: 13px;
  color: #546e7a;
  display: flex;
  gap: 10px;
}

.risk-tag {
  font-size: 12px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 4px;
  background: #eee;
}
.risk-tag.mild {
  color: #4caf50;
  background: #e8f5e9;
}
.risk-tag.moderate {
  color: #ffb300;
  background: #fff8e1;
}
.risk-tag.severe {
  color: #e53935;
  background: #ffebee;
}
.risk-tag.good {
  color: #00bcd4;
  background: #e0f7fa;
}

.card-summary h3 {
  font-size: 16px;
  color: #263238;
  margin: 0 0 12px 0;
}

.consultation-info {
  background: rgba(0, 0, 0, 0.02);
  border-radius: 8px;
  padding: 10px;
  display: flex;
  gap: 15px;
  font-size: 12px;
  flex-wrap: wrap;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 4px;
}
.info-item .label {
  color: #78909c;
}
.info-item .value {
  color: #263238;
  font-weight: 600;
}
.info-item .highlight {
  color: #00897b;
}
.text-gray {
  color: #90a4ae;
}

.card-action {
  width: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-left: 1px solid #f0f0f0;
}

.radio-indicator {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 2px solid #cfd8dc;
  display: flex;
  align-items: center;
  justify-content: center;
}
.active .radio-indicator {
  border-color: #00897b;
}
.radio-inner {
  width: 10px;
  height: 10px;
  background: #00897b;
  border-radius: 50%;
}

.footer-action {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  background: white;
  padding: 15px 20px;
  box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.05);
  transform: translateY(100%);
  transition: transform 0.3s ease;
}
.footer-action.visible {
  transform: translateY(0);
}

.footer-content {
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.selected-tip {
  color: #546e7a;
  font-size: 14px;
}
.selected-tip span {
  color: #00897b;
  font-weight: 600;
}

.start-btn {
  background: linear-gradient(135deg, #00897b, #00acc1);
  color: white;
  border: none;
  padding: 10px 24px;
  border-radius: 20px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s;
}
.start-btn:disabled {
  background: #cfd8dc;
  cursor: not-allowed;
}
.start-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 137, 123, 0.3);
}

.empty-state {
  text-align: center;
  padding: 60px 0;
  color: #90a4ae;
}
.empty-icon {
  font-size: 48px;
  margin-bottom: 10px;
}
.go-test-btn {
  margin-top: 15px;
  padding: 8px 20px;
  background: #00897b;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}
</style>
