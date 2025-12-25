// front/src/api/ai.ts
import api from './auth' // 复用封装好的 axios 实例

export interface ConsultationResponse {
  consultation_id: number
  sequence_number: number
  message: string
  status: 'ongoing' | 'finished'
  report?: string // 只有结束时才会有这个字段
}

// 1. 发起/开始问诊
export const startConsultation = async (reportId: number | string) => {
  const response = await api.post<ConsultationResponse>('/consultation/start', {
    report_id: reportId,
  })
  return response.data
}

// 2. 发送对话消息
export const chatConsultation = async (consultationId: number, content: string) => {
  const response = await api.post<ConsultationResponse>('/consultation/chat', {
    consultation_id: consultationId,
    content: content,
  })
  return response.data
}

// 3. 手动结束问诊
export const finishConsultation = async (consultationId: number) => {
  const response = await api.post<ConsultationResponse>('/consultation/finish', {
    consultation_id: consultationId,
  })
  return response.data
}

// 4. 获取历史问诊列表 (用于选择页)
export const getConsultationHistoryList = async (uid: number | string) => {
  const response = await api.get('/consultation/history', {
    params: { uid },
  })
  return response.data
}
