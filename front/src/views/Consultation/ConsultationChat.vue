<template>
  <div class="chat-container">
    <div class="chat-header">
      <div class="header-left">
        <el-button link @click="goBack">
          <el-icon><ArrowLeft /></el-icon> 返回
        </el-button>
        <span class="title">AI 深度问诊</span>
      </div>
      <div class="header-right">
        <el-button
          v-if="status === 'ongoing'"
          type="danger"
          size="small"
          plain
          @click="handleFinish"
        >
          结束对话并生成报告
        </el-button>
        <el-button v-else type="success" size="small" plain @click="showReportDialog = true">
          查看生成的报告
        </el-button>
      </div>
    </div>

    <div class="chat-content" ref="chatRef">
      <div v-if="loading && messages.length === 0" class="loading-wrapper">
        <el-icon class="is-loading" :size="30"><Loading /></el-icon>
        <p>AI 正在分析您的测评报告，准备病历中...</p>
      </div>

      <div v-for="(msg, index) in messages" :key="index" class="message-row" :class="msg.role">
        <div class="avatar">
          <el-avatar
            v-if="msg.role === 'ai'"
            :size="40"
            src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png"
          />
          <el-avatar v-else :size="40" :src="userAvatar" />
        </div>

        <div class="message-bubble">
          <div
            v-if="msg.role === 'ai'"
            class="markdown-body"
            v-html="renderMarkdown(msg.content)"
          ></div>
          <div v-else>{{ msg.content }}</div>
        </div>
      </div>
      <div style="height: 20px"></div>
    </div>

    <div class="chat-footer" v-if="status === 'ongoing'">
      <el-input
        v-model="inputMessage"
        placeholder="请进一步描述您的症状或感受..."
        :rows="3"
        type="textarea"
        resize="none"
        @keydown.enter.prevent="handleSend"
      />
      <div class="send-btn-wrapper">
        <el-button
          type="primary"
          @click="handleSend"
          :loading="sending"
          :disabled="!inputMessage.trim()"
        >
          发送 <el-icon class="el-icon--right"><Position /></el-icon>
        </el-button>
      </div>
    </div>

    <el-dialog
      v-model="showReportDialog"
      title="🩺 AI 问诊病历报告"
      width="700px"
      :close-on-click-modal="false"
      destroy-on-close
      center
    >
      <div class="report-content markdown-body" v-html="renderMarkdown(finalReport)"></div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showReportDialog = false">留在页面</el-button>
          <el-button type="primary" @click="viewHistory"> 去历史档案查看 </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Position, Loading } from '@element-plus/icons-vue'
import { startConsultation, chatConsultation, finishConsultation } from '@/api/ai'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

const route = useRoute()
const router = useRouter()
// 这里的 reportId 对应路由配置中的 :reportId
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
const status = ref<'ongoing' | 'finished'>('ongoing')
const consultationId = ref<number>(0)
const userAvatar = localStorage.getItem('avatar_url') || ''

const showReportDialog = ref(false)
const finalReport = ref('')

// Markdown 渲染
const renderMarkdown = (text: string) => {
  if (!text) return ''
  return DOMPurify.sanitize(marked.parse(text) as string)
}

// 自动滚动
const chatRef = ref<HTMLElement | null>(null)
const scrollToBottom = async () => {
  await nextTick()
  if (chatRef.value) {
    chatRef.value.scrollTop = chatRef.value.scrollHeight
  }
}

// 1. 初始化发起问诊
const initConsultation = async () => {
  try {
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

    // 如果 AI 判定对话可以结束
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

// 3. 手动结束问诊
const handleFinish = () => {
  ElMessageBox.confirm('您确定要结束当前对话吗？AI 将根据现有信息生成最终诊断报告。', '提示', {
    confirmButtonText: '确定结束',
    cancelButtonText: '继续问诊',
    type: 'warning',
  }).then(async () => {
    try {
      const res = await finishConsultation(consultationId.value)
      status.value = 'finished'
      finalReport.value = res.report || ''
      showReportDialog.value = true
      messages.value.push({
        role: 'ai',
        content: '**[系统消息]** 对话已手动结束，您可以查看上方的病历报告。',
      })
      scrollToBottom()
    } catch (error) {
      console.error('结束问诊失败', error)
    }
  })
}

onMounted(() => {
  initConsultation()
})
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 85vh;
  max-width: 1000px;
  margin: 20px auto;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.chat-header {
  padding: 15px 25px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fafafa;
}

.title {
  font-size: 18px;
  font-weight: bold;
  margin-left: 10px;
}

.chat-content {
  flex: 1;
  padding: 25px;
  overflow-y: auto;
  background: #f4f7f6;
}

.message-row {
  display: flex;
  margin-bottom: 25px;
  gap: 15px;
}
.message-row.user {
  flex-direction: row-reverse;
}

.message-bubble {
  max-width: 75%;
  padding: 14px 18px;
  border-radius: 12px;
  font-size: 15px;
  line-height: 1.6;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.message-row.ai .message-bubble {
  background: #ffffff;
  color: #333;
  border-top-left-radius: 0;
}

.message-row.user .message-bubble {
  background: #00897b;
  color: #fff;
  border-top-right-radius: 0;
}

.chat-footer {
  padding: 20px 25px;
  background: #fff;
  border-top: 1px solid #f0f0f0;
  position: relative;
}

.send-btn-wrapper {
  position: absolute;
  right: 40px;
  bottom: 35px;
}

.report-content {
  max-height: 50vh;
  overflow-y: auto;
  padding: 20px;
  background: #f9f9f9;
  border: 1px solid #eee;
  border-radius: 8px;
}

/* Markdown 内部样式 */
:deep(.markdown-body) h3 {
  margin-top: 0;
}
:deep(.markdown-body) ul {
  padding-left: 20px;
}
</style>
