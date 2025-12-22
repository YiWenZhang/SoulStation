<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-header">
        <h1>心灵驿站</h1>
        <p>欢迎回来，请登录</p>
      </div>

      <form @submit.prevent="handleLogin" class="auth-form">
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
          <label for="password">密码</label>
          <input
            type="password"
            id="password"
            v-model="password"
            placeholder="请输入密码"
            required
          />
        </div>

        <div v-if="error" class="error-message">{{ error }}</div>

        <button type="submit" class="auth-button" :disabled="authStore.loading">
          <span v-if="!authStore.loading">登录</span>
          <span v-else>登录中...</span>
        </button>

        <div class="auth-link">还没有账号？<router-link to="/register">立即注册</router-link></div>
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
const password = ref('')
const error = ref('')

const handleLogin = async () => {
  error.value = ''
  try {
    await authStore.login(phone.value, password.value)
  } catch (err) {
    console.error('登录失败:', err)
    error.value = authStore.error || '登录失败，请检查账号密码'
  }
}
</script>

<!-- 全局样式：改用视口单位，彻底重置默认样式 -->
<style>
/* 关键修改：用100vh/vw替代100%，确保不受父元素影响 */
html,
body {
  margin: 0 !important; /* 强制清零，优先级最高 */
  padding: 0 !important;
  height: 100vh; /* 视口高度，全屏必满 */
  width: 100vw; /* 视口宽度，全屏必满 */
  overflow: hidden; /* 禁用滚动条，避免挤占空间 */
  box-sizing: border-box;
}

/* Vue根容器强制撑满视口 */
#app {
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

/* 全局box-sizing，避免所有元素padding/border撑大尺寸 */
* {
  box-sizing: inherit;
}
</style>

<style scoped>
.auth-container {
  /* 核心修改：视口单位+绝对定位兜底，确保全屏覆盖 */
  position: relative; /* 兜底定位 */
  height: 100vh; /* 视口高度，全屏必满 */
  width: 100vw; /* 视口宽度，全屏必满 */
  display: flex;
  flex-direction: column;
  justify-content: center; /* 垂直居中 */
  align-items: center; /* 水平居中 */
  background: linear-gradient(135deg, #e0f7fa 0%, #b2ebf2 100%);
  padding: 20px 15px;
  margin: 0 !important; /* 强制清零margin，避免偏左 */
  overflow: hidden; /* 禁用内部滚动 */
}

.auth-card {
  width: 100%;
  max-width: 400px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  padding: 30px;
  margin: 0 auto; /* 兜底居中，解决flex兼容问题 */
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

/* 适配小屏幕（可选，增强兼容性） */
@media (max-width: 480px) {
  .auth-card {
    padding: 20px;
  }
  .auth-container {
    padding: 15px 10px;
  }
}
</style>
