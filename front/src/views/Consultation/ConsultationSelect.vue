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
      <div class="list-container" v-if="historyList.length > 0">
        <div
          v-for="item in historyList"
          :key="item.id"
          class="history-card"
          :class="{ active: selectedId === item.id }"
          @click="selectReport(item.id)"
        >
          <div class="status-bar" :class="item.risk_level"></div>

          <div class="card-body">
            <div class="card-header-info">
              <div class="meta-info">
                <span class="date">📅 {{ item.date }}</span>
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
                <span class="label">AI问诊次数:</span>
                <span class="value highlight">{{ item.consultation_count }}次</span>
              </div>
              <div class="info-item" v-if="item.last_consultation_time">
                <span class="icon">🕒</span>
                <span class="label">最近问诊:</span>
                <span class="value">{{ item.last_consultation_time }}</span>
              </div>
              <div class="info-item" v-else>
                <span class="icon">✨</span>
                <span class="value text-gray">尚未进行过问诊</span>
              </div>
            </div>
          </div>

          <div class="card-action">
            <div class="radio-indicator">
              <div class="radio-inner" v-if="selectedId === item.id"></div>
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
import { getHomeIndex, type HomeResponse } from '../../api/home'

// 1. 获取 API 返回的历史记录单项类型
type HomeHistoryItem = HomeResponse['data']['history_records'][0]

// 2. 定义扩展后的前端视图类型（包含模拟字段）
interface ConsultationHistoryItem extends HomeHistoryItem {
  mode_name: string
  consultation_count: number
  last_consultation_time: string | null
}

const router = useRouter()
// 3. 使用明确的类型替代 any[]
const historyList = ref<ConsultationHistoryItem[]>([])
const selectedId = ref<number | null>(null) // id 是 number 类型
const loading = ref(true)

// 获取数据
onMounted(async () => {
  const uid = localStorage.getItem('uid')
  if (!uid) return

  try {
    loading.value = true
    const res = await getHomeIndex(uid)

    if (res.code === 200) {
      // 映射并断言类型
      historyList.value = res.data.history_records.map((item) => {
        const extendedItem: ConsultationHistoryItem = {
          ...item,
          mode_name: item.mode === 'scale' ? '专业量表' : '快速测试',
          // 模拟数据
          consultation_count: Math.floor(Math.random() * 3),
          last_consultation_time: Math.random() > 0.5 ? '2025-06-01 14:00' : null,
        }
        return extendedItem
      })
    }
  } catch (error) {
    console.error('获取历史记录失败', error)
  } finally {
    loading.value = false
  }
})

// 辅助函数
const getRiskText = (level: string): string => {
  const map: Record<string, string> = {
    mild: '轻度关注',
    moderate: '中度风险',
    severe: '高风险',
    good: '状态良好',
  }
  return map[level] || '未知状态'
}

const getSelectedDate = computed(() => {
  const item = historyList.value.find((i) => i.id === selectedId.value)
  return item ? item.date : ''
})

// 交互方法
const goHome = () => router.push('/home')
const goTest = () => router.push('/assessment?mode=scale')

const selectReport = (id: number) => {
  selectedId.value = id
}

const startConsultation = () => {
  if (!selectedId.value) return

  // TODO: 这里实现后续的跳转逻辑，目前先打印
  console.log('开始问诊，选中的报告ID:', selectedId.value)
  // router.push(`/consultation/chat?report_id=${selectedId.value}`)
  alert('即将跳转到聊天界面，Report ID: ' + selectedId.value)
}
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background: #f8f9ff;
  display: flex;
  flex-direction: column;
  padding-bottom: 80px; /* 为底部栏留空 */
}

/* 头部样式 */
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

/* 列表样式 */
.main-content {
  flex: 1;
  max-width: 800px;
  margin: 20px auto;
  width: 100%;
  padding: 0 20px;
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

.card-summary h3 {
  font-size: 16px;
  color: #263238;
  margin: 0 0 12px 0;
}

/* 问诊信息区 */
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

/* 选择按钮 */
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

/* 底部操作栏 */
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
