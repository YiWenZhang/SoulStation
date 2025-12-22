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

        <div class="form-group checkbox-group">
          <label class="checkbox-label">
            <input type="checkbox" v-model="isAdmin" @change="handleAdminChange" />
            注册为管理员
          </label>
        </div>

        <div class="form-group" v-if="isAdmin" :class="{ 'admin-key-group': isAdmin }">
          <label for="adminKey">管理员密钥</label>
          <input
            type="text"
            id="adminKey"
            v-model="adminKey"
            placeholder="请输入管理员密钥"
            required
          />
        </div>

        <div v-if="error" class="error-message">{{ error }}</div>

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

const authStore = useAuthStore()
const phone = ref('')
const nickname = ref('')
const password = ref('')
const isAdmin = ref(false)
const adminKey = ref('')
const error = ref('')

const handleAdminChange = (e: Event) => {
  isAdmin.value = (e.target as HTMLInputElement).checked
  if (!isAdmin.value) {
    adminKey.value = ''
  }
}

const handleRegister = async () => {
  error.value = ''

  // 基本验证
  if (isAdmin.value && !adminKey.value) {
    error.value = '请输入管理员密钥'
    return
  }

  try {
    const userData: any = {
      phone: phone.value,
      password: password.value,
      nickname: nickname.value,
    }

    // 如果是管理员注册，添加角色和密钥
    if (isAdmin.value) {
      userData.role = 'admin'
      userData.admin_key = adminKey.value
    }

    await authStore.register(userData)
  } catch (err) {
    // 修复ESLint未使用变量警告
    console.error('注册失败:', err)
    error.value = authStore.error || '注册失败，请检查信息'
  }
}
</script>

<!-- 新增全局样式重置（和登录页保持一致） -->
<style>
/* 强制重置全局默认样式，确保全屏撑满 */
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
  /* 核心修改：视口单位+强制撑满，解决全屏问题 */
  height: 100vh;
  width: 100vw;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #e0f7fa 0%, #b2ebf2 100%);
  padding: 20px 15px;
  margin: 0 !important; /* 强制清零margin，解决偏左问题 */
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
  margin: 0 auto; /* 兜底居中，兼容所有浏览器 */
  box-sizing: border-box; /* 防止padding撑大卡片 */
}

.auth-header {
  text-align: center;
  margin-bottom: 30px;
}

.auth-header h1 {
  color: #00897b;
  margin-bottom: 10px;
  font-size: 28px;
  margin-top: 0; /* 清除默认margin */
}

.auth-header p {
  color: #546e7a;
  font-size: 16px;
  margin: 0; /* 清除默认margin */
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin: 0; /* 清除默认margin */
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

.checkbox-group {
  flex-direction: row;
  align-items: center;
  margin-top: 10px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #546e7a;
}

.checkbox-label input {
  width: 18px;
  height: 18px;
  accent-color: #00897b;
}

.admin-key-group {
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
  margin: 0; /* 清除默认margin */
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
  text-align: center; /* 确保版权信息居中 */
}

.auth-footer p {
  margin: 0; /* 清除默认margin */
}

/* 小屏幕适配（可选） */
@media (max-width: 480px) {
  .auth-card {
    padding: 20px;
  }
  .auth-container {
    padding: 15px 10px;
  }
}
</style>
