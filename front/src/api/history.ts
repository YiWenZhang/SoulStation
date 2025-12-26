// front/src/api/history.ts
import axios from 'axios'

// ==================== 类型定义 ====================

// 雷达图数据项
export interface RadarDataItem {
  name: string
  value: number
  fullMark: number
}

// 聊天消息类型
export interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
}

// 过滤后的聊天消息类型（不含 system）
export interface FilteredChatMessage {
  role: 'user' | 'assistant'
  content: string
}

// 通用 API 响应结构
export interface ApiResponse<T> {
  code: number
  msg: string
  data: T
}

// ==================== 问诊历史列表相关 ====================

// 问诊历史列表项 (GET /api/consultation/history)
export interface ConsultationHistoryItem {
  id: number                          // 报告ID
  date: string                        // 测评日期 YYYY-MM-DD
  mode: 'ai_chat' | 'scale'           // 测评模式
  mode_name: string                   // 模式名称
  risk_level: 'good' | 'moderate' | 'severe'  // 风险等级
  summary: string                     // 简短结论
  consultation_count: number          // 已问诊次数
  last_consultation_time: string | null  // 最近问诊时间
}

export type ConsultationHistoryResponse = ApiResponse<ConsultationHistoryItem[]>

// ==================== 问诊详情相关 ====================

// 分数变化记录 (维度名 -> 变化值)
export interface ScoreChanges {
  [dimension: string]: number
}

// AI修正后的分数 (维度名 -> 分数值)
export interface FinalScores {
  [dimension: string]: number
}

// 问诊详情数据 (GET /api/consultation/detail/<id>)
export interface ConsultationDetailData {
  id: number                          // 问诊ID
  report_id: number                   // 关联的报告ID
  sequence_number: number             // 第几次问诊
  diagnosis_summary: string | null    // Markdown格式的诊断总结
  initial_scores: RadarDataItem[]     // 原始问卷的雷达图分数
  final_scores: FinalScores | null    // AI问诊后修正的维度分数
  score_changes: ScoreChanges | null  // 相比初始分数的变化幅度
  initial_risk_level: 'good' | 'moderate' | 'severe' | null  // 初始风险等级
  final_risk_level: 'good' | 'moderate' | 'severe' | null    // 修正后风险等级
  status: 'finished' | 'ongoing'      // 问诊状态
  updated_at: string                  // 更新时间 YYYY-MM-DD HH:MM
  chat_history: ChatMessage[]         // 对话历史记录
}

export type ConsultationDetailResponse = ApiResponse<ConsultationDetailData>

// ==================== 发起问诊相关 ====================

// 发起问诊请求参数
export interface StartConsultationParams {
  report_id: number | string
}

// 发起问诊响应数据
export interface StartConsultationData {
  consultation_id: number
  sequence_number: number
  message: string                     // AI开场白
  status: 'ongoing'
  is_resume?: boolean                 // 是否为恢复之前的问诊
}

export type StartConsultationResponse = ApiResponse<StartConsultationData> & {
  consultation_id?: number
  sequence_number?: number
  message?: string
  status?: string
  is_resume?: boolean
}

// ==================== 对话交互相关 ====================

// 对话请求参数
export interface ChatConsultationParams {
  consultation_id: number | string
  content: string
}

// 对话响应数据
export interface ChatConsultationData {
  code: number
  message: string                     // AI回复内容
  status: 'ongoing' | 'finished'      // 对话状态
  consultation_id?: number            // 问诊结束时返回
  msg?: string                        // 附加消息
}

export type ChatConsultationResponse = ChatConsultationData

// ==================== 手动结束问诊相关 ====================

// 结束问诊请求参数
export interface FinishConsultationParams {
  consultation_id: number | string
}

// 结束问诊响应数据
export interface FinishConsultationData {
  consultation_id: number
  report_preview?: string             // 报告预览
}

export type FinishConsultationResponse = ApiResponse<FinishConsultationData> & {
  status?: 'finished'
}

// ==================== 兼容旧版历史记录接口 ====================

// 单次 AI 问诊记录 (用于历史列表展示)
export interface ConsultationItem {
  id: number
  sequence_number: number
  date: string
  summary_snippet: string
  status: string
}

// 历史测评报告 (用于历史列表展示)
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

export type HistoryListResponse = ApiResponse<HistoryItem[]>

// ==================== API 方法定义 ====================

/**
 * 获取问诊历史报告列表
 * GET /api/consultation/history?uid=xxx
 */
export const getConsultationHistory = async (
  uid: number | string
): Promise<ConsultationHistoryResponse> => {
  const response = await axios.get<ConsultationHistoryResponse>('/api/consultation/history', {
    params: { uid },
  })
  return response.data
}

/**
 * 获取问诊详细结果
 * GET /api/consultation/detail/<consultation_id>
 */
export const getConsultationDetail = async (
  consultationId: number | string
): Promise<ConsultationDetailResponse> => {
  const response = await axios.get<ConsultationDetailResponse>(
    `/api/consultation/detail/${consultationId}`
  )
  return response.data
}

/**
 * 发起问诊
 * POST /api/consultation/start
 */
export const startConsultation = async (
  params: StartConsultationParams
): Promise<StartConsultationResponse> => {
  const response = await axios.post<StartConsultationResponse>(
    '/api/consultation/start',
    params
  )
  // 后端直接返回数据，不包裹在 data 中
  return response.data
}

/**
 * 对话交互
 * POST /api/consultation/chat
 */
export const chatConsultation = async (
  params: ChatConsultationParams
): Promise<ChatConsultationResponse> => {
  const response = await axios.post<ChatConsultationResponse>(
    '/api/consultation/chat',
    params
  )
  return response.data
}

/**
 * 手动结束问诊
 * POST /api/consultation/finish
 */
export const finishConsultation = async (
  params: FinishConsultationParams
): Promise<FinishConsultationResponse> => {
  const response = await axios.post<FinishConsultationResponse>(
    '/api/consultation/finish',
    params
  )
  return response.data
}

// ==================== 兼容旧版 API ====================

/**
 * 获取历史测评记录列表 (旧版接口，保持兼容)
 * GET /api/history/list
 */
export const getHistoryList = async (
  uid: number | string
): Promise<HistoryListResponse> => {
  const response = await axios.get<HistoryListResponse>('/api/history/list', {
    params: { uid },
  })
  return response.data
}

// ==================== 辅助函数 ====================

/**
 * 过滤掉 system 角色的消息，只保留 user 和 assistant
 */
export const filterChatMessages = (messages: ChatMessage[]): FilteredChatMessage[] => {
  return messages
    .filter((msg): msg is ChatMessage & { role: 'user' | 'assistant' } =>
      msg.role === 'user' || msg.role === 'assistant'
    )
    .map((msg) => ({
      role: msg.role,
      content: msg.content,
    }))
}

/**
 * 获取风险等级对应的中文标签
 */
export const getRiskLevelLabel = (level: string | null | undefined): string => {
  const map: Record<string, string> = {
    good: '良好',
    moderate: '中等',
    severe: '高风险',
  }
  return map[level || 'good'] || '未知'
}

/**
 * 获取风险等级对应的样式类名
 */
export const getRiskLevelClass = (level: string | null | undefined): string => {
  const map: Record<string, string> = {
    good: 'risk-good',
    moderate: 'risk-moderate',
    severe: 'risk-severe',
  }
  return map[level || 'good'] || 'risk-good'
}

/**
 * 获取风险等级对应的 Emoji
 */
export const getRiskLevelEmoji = (level: string | null | undefined): string => {
  const map: Record<string, string> = {
    good: '😊',
    moderate: '😐',
    severe: '😟',
  }
  return map[level || 'good'] || '😊'
}
