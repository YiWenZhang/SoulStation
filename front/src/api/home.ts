import axios from 'axios'

// 定义首页接口响应类型（TS类型约束）
export interface HomeResponse {
  code: number
  msg: string
  data: {
    user_info: {
      nickname: string
      avatar_url: string
    }
    tracking_reminder: {
      show: boolean
      message: string
    }
    history_records: Array<{
      id: number
      date: string
      mode: string
      risk_level: string
      summary: string
    }>
  }
}

// 首页数据请求函数
export const getHomeIndex = async (uid: number | string): Promise<HomeResponse> => {
  try {
    const response = await axios.get('/api/home/index', {
      params: { uid }, // 传递必填的uid参数
    })
    return response.data
  } catch (error) {
    console.error('获取首页数据失败:', error)
    throw error // 抛出错误，让组件层捕获
  }
}
