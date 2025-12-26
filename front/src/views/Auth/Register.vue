<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-header">
        <h1>心灵驿站</h1>
        <p>创建账号，开始您的心灵之旅</p>
      </div>

      <form @submit.prevent="handleRegister" class="auth-form">
        <div class="form-group">
          <label for="phone">手机号</label>
          <input
            type="tel"
            id="phone"
            v-model="phone"
            placeholder="请输入手机号"
            required
            pattern="1[3-9]\d{9}"
          />
        </div>

        <div class="form-group">
          <label for="nickname">昵称</label>
          <input type="text" id="nickname" v-model="nickname" placeholder="请输入昵称" required />
        </div>

        <div class="form-group">
          <label for="password">密码</label>
          <input
            type="password"
            id="password"
            v-model="password"
            placeholder="请输入密码（至少6位）"
            required
            minlength="6"
          />
        </div>

        <div v-if="error" class="error-message">{{ error }}</div>
        <div v-if="success" class="success-message">{{ success }}</div>

        <button type="submit" class="auth-button" :disabled="authStore.loading">
          <span v-if="!authStore.loading">注册</span>
          <span v-else>注册中...</span>
        </button>

        <div class="auth-link">已有账号？<router-link to="/login">立即登录</router-link></div>
      </form>
    </div>

    <div class="auth-footer">
      <p>心灵驿站 © 2025 版权所有</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { useRouter } from 'vue-router'

// 注册参数类型
interface RegisterUserData {
  phone: string
  password: string
  nickname: string
}

const authStore = useAuthStore()
const router = useRouter()
const phone = ref('')
const nickname = ref('')
const password = ref('')
const error = ref('')
const success = ref('')

const handleRegister = async () => {
  error.value = ''
  success.value = ''

  try {
    const userData: RegisterUserData = {
      phone: phone.value,
      password: password.value,
      nickname: nickname.value,
    }

    // 调用注册接口
    const response = await authStore.register(userData)

    // 注册成功判断
    if (response.code === 200) {
      success.value = '注册成功！即将为您跳转到登录页...'
      // 延迟1.5秒跳转
      setTimeout(() => {
        router.push('/login')
        // 清空表单
        phone.value = ''
        nickname.value = ''
        password.value = ''
      }, 1500)
    }
  } catch (err) {
    console.error('注册失败:', err)
    error.value = authStore.error || '注册失败，请检查信息'
  }
}
</script>

<style>
html,
body {
  margin: 0 !important;
  padding: 0 !important;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  box-sizing: border-box;
}

#app {
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

* {
  box-sizing: inherit;
}
</style>

<style scoped>
.auth-container {
  height: 100vh;
  width: 100vw;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #e0f7fa 0%, #b2ebf2 100%);
  padding: 20px 15px;
  margin: 0 !important;
  overflow: hidden;
  box-sizing: border-box;
}

.auth-card {
  width: 100%;
  max-width: 400px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  padding: 30px;
  margin: 0 auto;
  box-sizing: border-box;
}

.auth-header {
  text-align: center;
  margin-bottom: 30px;
}

.auth-header h1 {
  color: #00897b;
  margin-bottom: 10px;
  font-size: 28px;
  margin-top: 0;
}

.auth-header p {
  color: #546e7a;
  font-size: 16px;
  margin: 0;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin: 0;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  color: #26a69a;
  font-weight: 500;
}

.form-group input {
  padding: 12px 15px;
  border: 1px solid #b2ebf2;
  border-radius: 6px;
  font-size: 16px;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.form-group input:focus {
  outline: none;
  border-color: #00acc1;
  box-shadow: 0 0 0 3px rgba(0, 172, 193, 0.2);
}

.auth-button {
  background-color: #00897b;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 14px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.auth-button:hover:not(:disabled) {
  background-color: #00695c;
}

.auth-button:disabled {
  background-color: #80cbc4;
  cursor: not-allowed;
}

.error-message {
  color: #e53935;
  font-size: 14px;
  text-align: center;
  padding: 10px;
  background-color: #ffebee;
  border-radius: 6px;
  margin: 0;
}

.success-message {
  color: #43a047;
  font-size: 14px;
  text-align: center;
  padding: 10px;
  background-color: #e8f5e9;
  border-radius: 6px;
  margin: 0;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.auth-link {
  text-align: center;
  margin-top: 15px;
  color: #546e7a;
}

.auth-link a {
  color: #00897b;
  text-decoration: none;
  font-weight: 500;
}

.auth-link a:hover {
  text-decoration: underline;
}

.auth-footer {
  margin-top: 30px;
  color: #546e7a;
  font-size: 14px;
  text-align: center;
}

.auth-footer p {
  margin: 0;
}

@media (max-width: 480px) {
  .auth-card {
    padding: 20px;
  }
  .auth-container {
    padding: 15px 10px;
  }
}
</style>
