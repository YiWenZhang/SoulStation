<template>
  <div class="detail-container">
    <header class="detail-header">
      <button class="nav-btn" @click="$router.back()">← 返回列表</button>
      <h2>问诊详情</h2>
      <div class="placeholder"></div>
    </header>

    <div v-if="loading" class="loading-box">
      <div class="spinner"></div>
      <p>正在加载详情...</p>
    </div>

    <div v-else-if="detail" class="detail-content">
      <div class="summary-card">
        <div class="card-title-row">
          <h3>📄 AI 诊断建议</h3>
          <span class="date-tag">{{ detail.date }}</span>
        </div>
        <div class="summary-text">{{ detail.diagnosis_report || '本次问诊暂无总结建议' }}</div>
      </div>

      <div class="chat-review">
        <h3 class="section-title">💬 对话回顾</h3>

        <div class="chat-list">
          <div v-if="!detail.chat_history || detail.chat_history.length === 0" class="empty-chat">
            暂无对话记录
          </div>

          <div
            v-for="(msg, index) in detail.chat_history"
            :key="index"
            class="message-row"
            :class="msg.role"
          >
            <div class="avatar">
              {{ msg.role === 'user' ? '👤' : '🤖' }}
            </div>
            <div class="bubble-container">
              <div class="sender-name">{{ msg.role === 'user' ? '我' : 'AI 咨询师' }}</div>
              <div class="bubble">
                {{ msg.content }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="error-state">
      <p>未找到该问诊记录</p>
      <button @click="$router.back()">返回</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getConsultationDetail, type ConsultationDetailResponse } from '@/api/history'

const route = useRoute()
const router = useRouter()
const loading = ref(true)
const detail = ref<ConsultationDetailResponse['data'] | null>(null)

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
</script>

<style scoped>
.detail-container {
  min-height: 100vh;
  background: #f5f7fa;
  display: flex;
  flex-direction: column;
}

.detail-header {
  background: white;
  padding: 15px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-btn {
  border: none;
  background: none;
  color: #00897b;
  font-size: 15px;
  cursor: pointer;
  font-weight: 500;
}

.detail-header h2 {
  font-size: 18px;
  color: #333;
  margin: 0;
}

.placeholder {
  width: 60px;
}

.loading-box,
.error-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #999;
  padding: 50px 0;
}

.spinner {
  width: 30px;
  height: 30px;
  border: 3px solid #e0f2f1;
  border-top-color: #00897b;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.detail-content {
  flex: 1;
  max-width: 800px;
  margin: 20px auto;
  width: 100%;
  padding: 0 20px;
  box-sizing: border-box;
}

/* 诊断总结卡片 */
.summary-card {
  background: white;
  border-radius: 12px;
  padding: 25px;
  margin-bottom: 25px;
  box-shadow: 0 4px 15px rgba(0, 137, 123, 0.08);
  border-left: 5px solid #00897b;
}

.card-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.summary-card h3 {
  color: #00897b;
  margin: 0;
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.date-tag {
  font-size: 12px;
  color: #999;
  background: #f5f5f5;
  padding: 4px 8px;
  border-radius: 4px;
}

.summary-text {
  color: #455a64;
  line-height: 1.8;
  white-space: pre-wrap;
  font-size: 15px;
  text-align: justify;
}

/* 聊天记录区域 */
.chat-review {
  margin-top: 30px;
}

.section-title {
  color: #78909c;
  font-size: 14px;
  margin-bottom: 20px;
  text-align: center;
  position: relative;
}

.section-title::before,
.section-title::after {
  content: '';
  display: inline-block;
  width: 30px;
  height: 1px;
  background: #cfd8dc;
  vertical-align: middle;
  margin: 0 10px;
}

.chat-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding-bottom: 40px;
}

.empty-chat {
  text-align: center;
  color: #ccc;
  font-size: 14px;
  padding: 20px;
}

.message-row {
  display: flex;
  gap: 12px;
  max-width: 85%;
}

.message-row.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.avatar {
  width: 36px;
  height: 36px;
  background: #eee;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.message-row.assistant .avatar {
  background: white;
  border: 1px solid #e0f2f1;
  color: #00897b;
}

.message-row.user .avatar {
  background: #00897b;
  color: white;
}

.bubble-container {
  display: flex;
  flex-direction: column;
}

.sender-name {
  font-size: 12px;
  color: #90a4ae;
  margin-bottom: 4px;
}

.message-row.user .sender-name {
  text-align: right;
}

.bubble {
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 15px;
  line-height: 1.6;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
  word-wrap: break-word;
}

.message-row.assistant .bubble {
  background: white;
  color: #37474f;
  border-top-left-radius: 2px;
}

.message-row.user .bubble {
  background: #e0f2f1;
  color: #00695c;
  border-top-right-radius: 2px;
}
</style>
