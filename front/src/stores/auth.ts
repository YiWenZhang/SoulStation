import { defineStore } from 'pinia'
import { login as loginApi, register as registerApi } from '../api/auth'
import router from '../router'

// 1. 定义用户信息类型（登录后存储的用户信息）
interface UserInfo {
  uid: string | number
  nickname: string
  avatar_url: string
}

// 2. 定义Auth State类型（Pinia状态的类型）
interface AuthState {
  user: UserInfo | null
  token: string | null
  role: string | null
  loading: boolean
  error: string | null
}

// 3. 定义注册参数类型（核心修复：role改为"admin"字面量类型）
interface RegisterUserData {
  phone: string
  password: string
  nickname: string
  role?: 'admin' // 仅能是"admin"（不是任意string），管理员注册时传
  admin_key?: string // 管理员密钥，仅管理员注册时传
}

// 4. 定义Axios错误类型（catch中err的类型）
interface AxiosError {
  response?: {
    data?: {
      msg: string
    }
  }
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    user: null,
    token: localStorage.getItem('token') || null,
    role: localStorage.getItem('role') || null,
    loading: false,
    error: null,
  }),

  actions: {
    // 登录
    async login(phone: string, password: string) {
      this.loading = true
      this.error = null
      try {
        const response = await loginApi(phone, password)
        if (response.code === 200) {
          const { uid, token, role, nickname, avatar_url } = response.data
          this.user = { uid, nickname, avatar_url }
          this.token = token
          this.role = role

          // 存储到localStorage（确保所有值都是字符串）
          localStorage.setItem('uid', String(uid))
          localStorage.setItem('token', token)
          localStorage.setItem('role', role)
          localStorage.setItem('nickname', nickname)
          localStorage.setItem('avatar_url', avatar_url || '')

          // 根据角色跳转
          if (role === 'admin') {
            router.push('/admin/dashboard')
          } else {
            router.push('/home')
          }
        }
        return response
      } catch (err) {
        const error = err as AxiosError
        this.error = error.response?.data?.msg || '登录失败，请重试'
        throw err
      } finally {
        this.loading = false
      }
    },

    // 注册：参数类型严格匹配registerApi的要求
    // auth.ts 中 register 方法修改后
    async register(userData: RegisterUserData) {
      this.loading = true
      this.error = null
      try {
        const response = await registerApi(userData)
        // 移除这行：router.push('/login')
        return response // 保留返回值，让页面判断是否成功
      } catch (err) {
        const error = err as AxiosError
        this.error = error.response?.data?.msg || '注册失败，请重试'
        throw err
      } finally {
        this.loading = false
      }
    },

    // 退出登录
    logout() {
      this.user = null
      this.token = null
      this.role = null

      // 清除localStorage
      localStorage.removeItem('uid')
      localStorage.removeItem('token')
      localStorage.removeItem('role')
      localStorage.removeItem('nickname')
      localStorage.removeItem('avatar_url')

      router.push('/login')
    },
  },
})
