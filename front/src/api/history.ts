// front/src/api/history.ts
import axios from 'axios'

// 1. 定义子项：单次 AI 问诊记录
export interface ConsultationItem {
  id: number
  sequence_number: number
  date: string
  summary_snippet: string
  status: string
}

// 2. 定义主项：历史测评报告
export interface HistoryItem {
  report_id: number
  report_date: string
  mode: string
  mode_name: string
  risk_level: string
  summary: string
  total_score: number
  consultations: ConsultationItem[]
}

// 3. 定义聊天记录的消息类型
export interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
  [key: string]: unknown
}

// 4. 定义通用 Response 结构
export interface ApiResponse<T> {
  code: number
  msg: string
  data: T
}

// 5. 定义具体的数据返回类型
export type HistoryListResponse = ApiResponse<HistoryItem[]>

export type ConsultationDetailResponse = ApiResponse<{
  id: number
  sequence_number: number
  date: string
  chat_history: ChatMessage[]
  diagnosis_report: string
  report_id: number
}>

// --- API 方法定义 ---

// 获取历史测评记录列表
export const getHistoryList = async (uid: number | string): Promise<HistoryListResponse> => {
  const response = await axios.get<HistoryListResponse>('/api/history/list', {
    params: { uid },
  })
  return response.data
}

// 获取单次问诊详情
export const getConsultationDetail = async (
  consultationId: number | string,
): Promise<ConsultationDetailResponse> => {
  const response = await axios.get<ConsultationDetailResponse>('/api/history/consultation/detail', {
    params: { id: consultationId },
  })
  return response.data
}
