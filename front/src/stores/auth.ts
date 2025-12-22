import { defineStore } from 'pinia'
import { login as loginApi, register as registerApi } from '../api/auth'
import router from '../router'

export const useAuthStore = defineStore('auth', {
  state: () => ({
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

          // 存储到localStorage
          localStorage.setItem('uid', uid)
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
        this.error = err.response?.data?.msg || '登录失败，请重试'
        throw err
      } finally {
        this.loading = false
      }
    },

    // 注册
    async register(userData: any) {
      this.loading = true
      this.error = null
      try {
        const response = await registerApi(userData)
        if (response.code === 200) {
          // 注册成功后跳转到登录页
          router.push('/login')
        }
        return response
      } catch (err) {
        this.error = err.response?.data?.msg || '注册失败，请重试'
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
