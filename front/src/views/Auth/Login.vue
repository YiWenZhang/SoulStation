<template>
  <div class="auth-container">
    <!-- 背景装饰元素 -->
    <div class="background-decoration">
      <div class="bubble bubble-1"></div>
      <div class="bubble bubble-2"></div>
      <div class="bubble bubble-3"></div>
      <div class="floating-heart heart-1">💖</div>
      <div class="floating-heart heart-2">🧘</div>
      <div class="floating-heart heart-3">🌱</div>
      <div class="wave wave-1"></div>
      <div class="wave wave-2"></div>
    </div>

    <!-- 主卡片 -->
    <div class="auth-card">
      <!-- 左侧装饰区域 -->
      <div class="card-decoration">
        <div class="decoration-circle">
          <div class="decoration-icon">🧠</div>
        </div>
        <div class="welcome-message">
          <h3>欢迎回到</h3>
          <h2>心灵驿站</h2>
          <p>您的心理健康成长伙伴</p>
        </div>
      </div>

      <!-- 右侧登录表单区域 -->
      <div class="card-form">
        <div class="form-header">
          <div class="header-icon">🔐</div>
          <h1>欢迎回来</h1>
          <p>请登录您的账户</p>
        </div>

        <form @submit.prevent="handleLogin" class="auth-form">
          <div class="form-group">
            <label for="phone" class="form-label">手机号</label>
            <div class="input-wrapper">
              <span class="input-icon">📱</span>
              <input
                type="tel"
                id="phone"
                v-model="phone"
                placeholder="请输入手机号"
                required
                pattern="1[3-9]\d{9}"
                class="form-input"
              />
            </div>
            <div class="input-hint">请输入11位手机号</div>
          </div>

          <div class="form-group">
            <label for="password" class="form-label">密码</label>
            <div class="input-wrapper">
              <span class="input-icon">🔒</span>
              <input
                :type="showPassword ? 'text' : 'password'"
                id="password"
                v-model="password"
                placeholder="请输入密码"
                required
                class="form-input"
              />
              <button type="button" class="password-toggle" @click="togglePasswordVisibility">
                <span class="toggle-icon">{{ showPassword ? '👁️' : '👁️‍🗨️' }}</span>
              </button>
            </div>
            <div class="input-hint">至少6位字符，区分大小写</div>
          </div>

          <!-- 记住我选项 -->
          <div class="form-options">
            <label class="checkbox-wrapper">
              <input type="checkbox" v-model="rememberMe" />
              <span class="checkbox-custom"></span>
              <span class="checkbox-label">记住我</span>
            </label>
          </div>

          <!-- 错误消息 -->
          <div v-if="error" class="error-message">
            <span class="error-icon">⚠️</span>
            {{ error }}
          </div>

          <!-- 登录按钮 -->
          <button
            type="submit"
            class="auth-button"
            :disabled="authStore.loading"
            :class="{ loading: authStore.loading }"
          >
            <span v-if="!authStore.loading">
              <span class="btn-icon">🚀</span>
              登录
            </span>
            <span v-else class="loading-content">
              <span class="loading-spinner"></span>
              登录中...
            </span>
          </button>

          <!-- 注册链接 -->
          <div class="auth-link">
            <span>还没有账号？</span>
            <router-link to="/register" class="register-link">
              <span class="link-icon">✨</span>
              立即注册
            </router-link>
          </div>
        </form>
      </div>
    </div>

    <!-- 页脚 -->
    <div class="auth-footer">
      <p class="footer-text">
        <span class="copyright-icon">©</span> 2025 心灵驿站 · 您的心理健康成长伙伴
      </p>
      <p class="footer-subtext">我们关心您的每一份情感</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()
const phone = ref('')
const password = ref('')
const error = ref('')
const rememberMe = ref(false)
const showPassword = ref(false)

// 密码可见性切换
const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value
}

// 登录处理
const handleLogin = async () => {
  error.value = ''
  try {
    await authStore.login(phone.value, password.value)
    // 如果记住我被选中，保存手机号
    if (rememberMe.value) {
      localStorage.setItem('remembered_phone', phone.value)
    } else {
      localStorage.removeItem('remembered_phone')
    }
    // 登录成功后跳转
    router.push('/home')
  } catch (err) {
    console.error('登录失败:', err)
    error.value = authStore.error || '登录失败，请检查账号密码'
  }
}

// 页面加载时检查记住我
onMounted(() => {
  const savedPhone = localStorage.getItem('remembered_phone')
  if (savedPhone) {
    phone.value = savedPhone
    rememberMe.value = true
  }
})
</script>

<style>
/* 全局样式 */
html,
body {
  margin: 0 !important;
  padding: 0 !important;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  font-family:
    -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

#app {
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

* {
  box-sizing: border-box;
}
</style>

<style scoped>
/* 主容器 */
.auth-container {
  position: relative;
  height: 100vh;
  width: 100vw;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 30%, #f1f8e9 70%, #e0f7fa 100%);
  padding: 20px;
  overflow: hidden;
}

/* 背景装饰 */
.background-decoration {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
}

.bubble {
  position: absolute;
  border-radius: 50%;
  background: radial-gradient(
    circle at 30% 30%,
    rgba(255, 255, 255, 0.3) 0%,
    rgba(255, 255, 255, 0.1) 50%,
    transparent 70%
  );
  animation: float 25s infinite ease-in-out;
  filter: blur(2px);
}

.bubble-1 {
  width: 300px;
  height: 300px;
  top: -100px;
  left: -100px;
  animation-delay: 0s;
}

.bubble-2 {
  width: 250px;
  height: 250px;
  bottom: -50px;
  right: -50px;
  animation-delay: -8s;
}

.bubble-3 {
  width: 180px;
  height: 180px;
  top: 50%;
  left: 70%;
  animation-delay: -16s;
}

.floating-heart {
  position: absolute;
  font-size: 24px;
  opacity: 0.15;
  animation: float-heart 20s infinite ease-in-out;
}

.heart-1 {
  top: 15%;
  left: 10%;
  animation-delay: 0s;
}

.heart-2 {
  top: 70%;
  left: 85%;
  animation-delay: -5s;
}

.heart-3 {
  top: 85%;
  left: 15%;
  animation-delay: -10s;
}

.wave {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 80px;
  background: linear-gradient(
    90deg,
    rgba(0, 137, 123, 0.08) 0%,
    rgba(156, 39, 176, 0.08) 50%,
    rgba(76, 175, 80, 0.08) 100%
  );
  border-radius: 100% 100% 0 0;
}

.wave-1 {
  height: 60px;
  opacity: 0.3;
  animation: wave 15s infinite linear;
}

.wave-2 {
  height: 40px;
  opacity: 0.2;
  animation: wave 12s infinite linear reverse;
}

@keyframes float {
  0%,
  100% {
    transform: translate(0, 0) rotate(0deg);
  }
  33% {
    transform: translate(30px, -50px) rotate(120deg);
  }
  66% {
    transform: translate(-20px, 30px) rotate(240deg);
  }
}

@keyframes float-heart {
  0%,
  100% {
    transform: translateY(0) rotate(0deg);
    opacity: 0.15;
  }
  50% {
    transform: translateY(-25px) rotate(180deg);
    opacity: 0.08;
  }
}

@keyframes wave {
  0% {
    transform: translateX(0);
  }
  100% {
    transform: translateX(-50%);
  }
}

/* 主卡片 - 调整高度和比例 */
.auth-card {
  position: relative;
  z-index: 1;
  width: 900px;
  height: 500px; /* 降低高度 */
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 24px;
  box-shadow:
    0 20px 60px rgba(0, 137, 123, 0.15),
    0 8px 32px rgba(0, 0, 0, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.6);
  display: flex;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.8);
  animation: card-enter 0.8s cubic-bezier(0.22, 1, 0.36, 1);
}

@keyframes card-enter {
  from {
    opacity: 0;
    transform: translateY(30px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* 左侧装饰区域 - 调整高度 */
.card-decoration {
  flex: 0 0 40%; /* 减少左侧宽度比例 */
  background: linear-gradient(135deg, #00897b 0%, #26a69a 50%, #4db6ac 100%);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 30px; /* 减少内边距 */
  position: relative;
  overflow: hidden;
}

.card-decoration::before {
  content: '';
  position: absolute;
  inset: 0;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><path d="M0,0 L100,0 L100,100 Z" fill="white" opacity="0.05"/></svg>');
  background-size: cover;
}

.decoration-circle {
  width: 140px; /* 减小尺寸 */
  height: 140px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.2) 0%, rgba(255, 255, 255, 0.1) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 30px; /* 减少间距 */
  border: 2px solid rgba(255, 255, 255, 0.3);
  animation: pulse 4s infinite ease-in-out;
}

@keyframes pulse {
  0%,
  100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.05);
    opacity: 0.8;
  }
}

.decoration-icon {
  font-size: 60px; /* 减小图标 */
  color: white;
}

.welcome-message {
  text-align: center;
  color: white;
  margin-top: 15px;
}

.welcome-message h3 {
  font-size: 16px;
  font-weight: 400;
  opacity: 0.9;
  margin: 0 0 8px;
}

.welcome-message h2 {
  font-size: 26px; /* 减小字体 */
  font-weight: 700;
  margin: 0 0 12px;
  letter-spacing: 0.5px;
}

.welcome-message p {
  font-size: 14px;
  opacity: 0.8;
  margin: 0;
  font-weight: 300;
}

/* 右侧表单区域 - 重点调整 */
.card-form {
  flex: 1;
  padding: 35px 40px; /* 减少内边距，让内容更靠上 */
  display: flex;
  flex-direction: column;
  justify-content: flex-start; /* 内容顶部对齐 */
  overflow-y: auto; /* 允许滚动 */
}

/* 表单头部 */
.form-header {
  text-align: center;
  margin-bottom: 30px; /* 减少底部间距 */
  margin-top: 0;
}

.header-icon {
  font-size: 36px; /* 减小图标 */
  margin-bottom: 12px;
  opacity: 0.8;
}

.form-header h1 {
  font-size: 24px;
  font-weight: 700;
  color: #263238;
  margin: 0 0 6px;
}

.form-header p {
  color: #78909c;
  font-size: 14px;
  margin: 0;
}

/* 表单样式 */
.auth-form {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.form-group {
  margin-bottom: 24px; /* 减少间距 */
}

/* 修正：将标签移到输入框上方 */
.form-label {
  display: block;
  color: #263238;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 8px;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  padding: 0 16px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  background: white;
  height: 52px; /* 减小高度 */
}

.input-wrapper:focus-within {
  border-color: #00897b;
  box-shadow: 0 0 0 3px rgba(0, 137, 123, 0.15);
}

.input-icon {
  font-size: 18px;
  margin-right: 12px;
  color: #78909c;
  transition: color 0.3s;
}

.input-wrapper:focus-within .input-icon {
  color: #00897b;
}

.form-input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 15px;
  height: 100%;
  background: transparent;
  color: #263238;
  padding: 0;
}

.form-input::placeholder {
  color: #b0bec5;
}

.password-toggle {
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
  font-size: 18px;
  color: #78909c;
  transition: color 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border-radius: 6px;
  margin-left: 8px;
}

.password-toggle:hover {
  color: #00897b;
  background: rgba(0, 137, 123, 0.1);
}

.input-hint {
  font-size: 12px;
  color: #90a4ae;
  margin-top: 6px;
  margin-left: 4px;
}

/* 表单选项 */
.form-options {
  display: flex;
  align-items: center;
  margin-bottom: 20px; /* 减少间距 */
}

.checkbox-wrapper {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.checkbox-wrapper input {
  display: none;
}

.checkbox-custom {
  width: 18px;
  height: 18px;
  border: 2px solid #b0bec5;
  border-radius: 4px;
  margin-right: 8px;
  position: relative;
  transition: all 0.3s;
}

.checkbox-wrapper input:checked + .checkbox-custom {
  background: #00897b;
  border-color: #00897b;
}

.checkbox-wrapper input:checked + .checkbox-custom::after {
  content: '';
  position: absolute;
  top: 2px;
  left: 5px;
  width: 4px;
  height: 8px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.checkbox-label {
  color: #546e7a;
  font-size: 14px;
}

/* 错误消息 */
.error-message {
  background: linear-gradient(135deg, rgba(244, 67, 54, 0.1) 0%, rgba(239, 83, 80, 0.1) 100%);
  color: #e53935;
  padding: 12px 14px;
  border-radius: 10px;
  margin-bottom: 20px;
  font-size: 13px;
  display: flex;
  align-items: center;
  border: 1px solid rgba(244, 67, 54, 0.2);
  animation: shake 0.5s cubic-bezier(0.36, 0, 0.66, -0.56);
}

@keyframes shake {
  0%,
  100% {
    transform: translateX(0);
  }
  25% {
    transform: translateX(-5px);
  }
  75% {
    transform: translateX(5px);
  }
}

.error-icon {
  margin-right: 8px;
  font-size: 16px;
}

/* 登录按钮 */
.auth-button {
  background: linear-gradient(135deg, #00897b 0%, #26a69a 50%, #4db6ac 100%);
  color: white;
  border: none;
  border-radius: 12px;
  padding: 16px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  margin-bottom: 20px;
  margin-top: 10px;
}

.auth-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 137, 123, 0.3);
}

.auth-button:active:not(:disabled) {
  transform: translateY(0);
}

.auth-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.auth-button.loading {
  background: linear-gradient(135deg, #80cbc4 0%, #a5d6a7 50%, #c8e6c9 100%);
}

.btn-icon {
  margin-right: 8px;
}

.loading-content {
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s linear infinite;
  margin-right: 10px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 注册链接 */
.auth-link {
  text-align: center;
  margin: 15px 0;
  color: #546e7a;
  font-size: 14px;
}

.register-link {
  color: #00897b;
  text-decoration: none;
  font-weight: 600;
  margin-left: 6px;
  display: inline-flex;
  align-items: center;
  transition: all 0.3s;
}

.register-link:hover {
  color: #00695c;
  text-decoration: underline;
}

.link-icon {
  margin-right: 6px;
  font-size: 13px;
}

/* 页脚 */
.auth-footer {
  position: absolute;
  bottom: 20px;
  left: 0;
  right: 0;
  text-align: center;
  z-index: 1;
}

.footer-text {
  color: rgba(255, 255, 255, 0.8);
  font-size: 13px;
  margin: 0 0 6px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.copyright-icon {
  opacity: 0.8;
}

.footer-subtext {
  color: rgba(255, 255, 255, 0.6);
  font-size: 11px;
  margin: 0;
  font-weight: 300;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

/* 响应式设计 */
@media (max-width: 1000px) {
  .auth-card {
    width: 90%;
    height: auto;
    min-height: 480px;
  }
}

@media (max-width: 768px) {
  .auth-card {
    flex-direction: column;
    height: auto;
    width: 95%;
    max-height: 90vh;
  }

  .card-decoration {
    flex: none;
    height: 200px;
    padding: 20px;
  }

  .decoration-circle {
    width: 100px;
    height: 100px;
    margin-bottom: 15px;
  }

  .decoration-icon {
    font-size: 45px;
  }

  .welcome-message h2 {
    font-size: 22px;
  }

  .card-form {
    padding: 25px 20px;
    max-height: calc(90vh - 200px);
    overflow-y: auto;
  }

  .form-header h1 {
    font-size: 22px;
  }
}

@media (max-width: 480px) {
  .auth-container {
    padding: 15px 10px;
  }

  .auth-card {
    width: 100%;
    border-radius: 18px;
  }

  .bubble-1,
  .bubble-2,
  .bubble-3 {
    display: none;
  }

  .floating-heart {
    font-size: 18px;
  }

  .card-decoration {
    padding: 15px;
    height: 180px;
  }

  .card-form {
    padding: 20px 15px;
    max-height: calc(90vh - 180px);
  }

  .input-wrapper {
    height: 48px;
    padding: 0 12px;
  }

  .auth-footer {
    bottom: 15px;
  }

  .footer-text {
    font-size: 12px;
  }
}
</style>
