// front/src/api/ai.ts
import api from './auth' // 复用封装好的 axios 实例

// ==================== 类型定义 ====================

export interface ConsultationResponse {
  consultation_id: number
  sequence_number: number
  message: string
  status: 'ongoing' | 'finished'
  is_resume?: boolean // 是否为恢复之前的问诊
  report?: string // 只有结束时才会有这个字段
}

export interface FinishConsultationResponse {
  code: number
  status: 'finished'
  msg: string
  data: {
    consultation_id: number
    report_preview?: string
  }
  report?: string // 可选字段，兼容旧版本
}

// 流式消息类型
export interface StreamMessage {
  type: 'message' | 'finished' | 'error' | 'done'
  content: string | StreamFinishedContent
}

export interface StreamFinishedContent {
  consultation_id?: number
  report?: string
  summary?: string
  msg?: string
}

// 流式回调函数类型
export interface StreamCallbacks {
  onMessage?: (content: string) => void // 收到消息片段
  onFinished?: (data: StreamFinishedContent) => void // 对话结束
  onError?: (error: string) => void // 发生错误
  onDone?: () => void // 流结束
}

// ==================== API 函数 ====================

/**
 * 1. 发起/开始问诊
 * POST /api/consultation/start
 */
export const startConsultation = async (
  reportId: number | string,
): Promise<ConsultationResponse> => {
  const response = await api.post<ConsultationResponse>('/consultation/start', {
    report_id: reportId,
  })
  return response.data
}

/**
 * 2. 发送对话消息（非流式，保留兼容）
 * POST /api/consultation/chat
 */
export const chatConsultation = async (
  consultationId: number,
  content: string,
): Promise<ConsultationResponse> => {
  const response = await api.post<ConsultationResponse>('/consultation/chat', {
    consultation_id: consultationId,
    content: content,
  })
  return response.data
}

/**
 * 3. 发送对话消息（流式版本）
 * POST /api/consultation/chat/stream
 * 使用 fetch API 处理 SSE 流
 */
export const chatConsultationStream = async (
  consultationId: number,
  content: string,
  callbacks: StreamCallbacks,
): Promise<void> => {
  const baseURL = api.defaults.baseURL || ''
  const url = `${baseURL}/consultation/chat/stream`

  // 获取认证 token（如果有的话）
  const token = localStorage.getItem('token')

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        consultation_id: consultationId,
        content: content,
      }),
    })

    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`)
    }

    const reader = response.body?.getReader()
    const decoder = new TextDecoder()

    if (!reader) {
      throw new Error('无法获取响应流')
    }

    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()

      if (done) {
        callbacks.onDone?.()
        break
      }

      buffer += decoder.decode(value, { stream: true })

      // 处理 SSE 数据，按行分割
      const lines = buffer.split('\n')
      buffer = lines.pop() || '' // 保留最后一个可能不完整的行

      for (const line of lines) {
        const trimmedLine = line.trim()

        if (!trimmedLine) continue

        if (trimmedLine.startsWith('data: ')) {
          const jsonStr = trimmedLine.slice(6) // 去掉 'data: ' 前缀

          if (!jsonStr) continue

          try {
            const data: StreamMessage = JSON.parse(jsonStr)

            switch (data.type) {
              case 'message':
                // 收到消息片段
                if (typeof data.content === 'string') {
                  callbacks.onMessage?.(data.content)
                }
                break

              case 'finished':
                // 对话结束
                if (typeof data.content === 'object') {
                  callbacks.onFinished?.(data.content)
                } else if (typeof data.content === 'string') {
                  callbacks.onFinished?.({ summary: data.content })
                }
                break

              case 'error':
                // 发生错误
                const errorMsg = typeof data.content === 'string' ? data.content : '发生未知错误'
                callbacks.onError?.(errorMsg)
                break

              case 'done':
                // 流结束信号
                callbacks.onDone?.()
                break
            }
          } catch (e) {
            console.error('解析 SSE 数据失败:', e, jsonStr)
          }
        }
      }
    }
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : '网络请求失败'
    callbacks.onError?.(errorMessage)
    throw error
  }
}

/**
 * 4. 获取流式对话的 URL（供直接使用 fetch 的场景）
 */
export const getChatStreamUrl = (): string => {
  const baseURL = api.defaults.baseURL || ''
  return `${baseURL}/consultation/chat/stream`
}

/**
 * 5. 手动结束问诊
 * POST /api/consultation/finish
 */
export const finishConsultation = async (
  consultationId: number,
): Promise<FinishConsultationResponse> => {
  const response = await api.post<FinishConsultationResponse>('/consultation/finish', {
    consultation_id: consultationId,
  })
  return response.data
}

/**
 * 6. 获取历史问诊列表 (用于选择页)
 * GET /api/consultation/history
 */
export const getConsultationHistoryList = async (uid: number | string) => {
  const response = await api.get('/consultation/history', {
    params: { uid },
  })
  return response.data
}

/**
 * 7. 获取问诊详情
 * GET /api/consultation/detail/<id>
 */
export const getConsultationDetail = async (consultationId: number | string) => {
  const response = await api.get(`/consultation/detail/${consultationId}`)
  return response.data
}
