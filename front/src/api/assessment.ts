import axios from 'axios'

// --- 类型定义 ---
export interface Option {
  id: number
  label: string
  score: number
}

export interface Question {
  id: number
  stem: string
  type: string
  options: Option[]
}

export interface StartResponse {
  session_id: number
  status: string
  is_resumed: boolean
  current_progress_index: number
  answers_snapshot: Record<string, number>
}

export interface SubmitResponse {
  report_id?: number
  total?: number
  answered?: number
}

// --- API 方法 ---

// 1. 初始化/检查状态
export const startAssessment = async (uid: number, action: 'check' | 'new' = 'check') => {
  const res = await axios.post('/api/assessment/questionnaire/start', { uid, action })
  return res.data
}

// 2. 获取全量题目 (就是这里！一定要有 export)
export const fetchQuestions = async () => {
  const res = await axios.get('/api/assessment/questionnaire/questions')
  return res.data
}

// 3. 实时保存进度
export const saveProgress = async (
  sessionId: number,
  currentIndex: number,
  answers: Record<string, number>,
) => {
  return axios.post('/api/assessment/questionnaire/save', {
    session_id: sessionId,
    current_index: currentIndex,
    answers,
  })
}

// 4. 提交并生成报告
export const submitAssessment = async (sessionId: number) => {
  const res = await axios.post('/api/assessment/questionnaire/submit', {
    session_id: sessionId,
  })
  return res.data
}
// 在 assessment.ts 中添加以下接口和方法
export interface ReportDetailResponse {
  base_info: {
    report_no: string
    date: string
    user_name: string
    mode_name: string
  }
  core_result: {
    risk_level: 'good' | 'moderate' | 'severe'
    risk_color: string
    summary_label: string
    score_interpretation: string
  }
  charts: {
    radar_data: Array<{
      name: string
      value: number
      fullMark: number
    }>
  }
  content: {
    advice_md: string
  }
  actions: {
    can_chat: boolean
    can_download: boolean
  }
}

// 获取测评报告详情
export const getReportDetail = async (reportId: string, uid: number) => {
  const res = await axios.get('/api/assessment/report/detail', {
    params: { report_id: reportId, uid },
  })
  return res.data
}
