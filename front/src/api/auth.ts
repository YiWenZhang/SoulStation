import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

// 创建axios实例
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 登录请求
export const login = async (phone: string, password: string) => {
  const response = await api.post('/auth/login', {
    phone,
    password,
  })
  return response.data
}

// 注册请求
export const register = async (userData: {
  phone: string
  password: string
  nickname: string
  role?: 'admin'
  admin_key?: string
}) => {
  const response = await api.post('/auth/register', userData)
  return response.data
}

// 获取当前用户信息
export const getCurrentUser = async () => {
  const token = localStorage.getItem('token')
  const response = await api.get('/auth/me', {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })
  return response.data
}

export default api
