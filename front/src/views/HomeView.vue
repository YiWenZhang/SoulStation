<template>
  <div class="home-container">
    <!-- 装饰性背景元素 -->
    <div class="background-decoration">
      <div class="bubble bubble-1"></div>
      <div class="bubble bubble-2"></div>
      <div class="bubble bubble-3"></div>
      <div class="bubble bubble-4"></div>
      <div class="leaf leaf-1">🍃</div>
      <div class="leaf leaf-2">🍃</div>
      <div class="leaf leaf-3">🍃</div>
    </div>

    <!-- 顶部导航栏 -->
    <header class="home-header">
      <div class="header-container">
        <div class="header-left">
          <div class="logo-container">
            <div class="logo-icon">🌸</div>
            <div class="logo-text-container">
              <h1 class="logo-text">心灵驿站</h1>
              <div class="logo-subtitle">Mental Harbor</div>
            </div>
          </div>
        </div>
        <div class="header-right">
          <!-- 用户信息和退出按钮向左移动 -->
          <div class="user-info-area">
            <div class="user-info" @click.stop="showUserMenu = !showUserMenu">
              <img :src="userInfo.avatar_url || defaultAvatar" alt="用户头像" class="avatar" />
              <div class="user-details">
                <span class="nickname">{{ userInfo.nickname }}</span>
                <span class="user-status">
                  <span class="status-dot"></span>
                  在线
                </span>
              </div>
              <div class="dropdown-arrow" :class="{ 'rotate-180': showUserMenu }">▼</div>

              <transition name="slide-fade">
                <div v-if="showUserMenu" class="user-menu" @click.stop>
                  <div class="menu-item" @click="gotoProfile">
                    <span class="menu-icon">👤</span>
                    <span>个人资料</span>
                  </div>

                  <div class="menu-item" @click="gotoHistory">
                    <span class="menu-icon">📂</span>
                    <span>历史档案</span>
                  </div>

                  <div class="menu-divider"></div>

                  <div class="menu-item logout-item" @click="handleLogout">
                    <span class="menu-icon">🚪</span>
                    <span>退出登录</span>
                  </div>
                </div>
              </transition>
            </div>
            <!-- <button class="logout-btn" @click="handleLogout">
              <span class="btn-icon">🚪</span>
              <span class="btn-text">退出</span>
            </button> -->
          </div>
        </div>
      </div>
    </header>

    <!-- 核心内容区 -->
    <main class="home-main">
      <!-- 欢迎语 -->
      <div class="welcome-section">
        <div class="welcome-content">
          <h2 class="welcome-title">
            欢迎回来，<span class="highlight">{{ userInfo.nickname }}</span> 👋
          </h2>
          <p class="welcome-subtitle">今天的心情如何？让我们一起来关注您的心理健康</p>
        </div>
        <div class="welcome-decoration">
          <div class="quote-box">
            <div class="quote-icon">💭</div>
            <p class="quote-text">"心理健康是健康生活的重要组成部分"</p>
          </div>
        </div>
      </div>

      <!-- 复测提醒Banner（条件渲染） -->
      <div v-if="trackingReminder.show" class="tracking-banner">
        <div class="banner-content">
          <div class="banner-icon-wrapper">
            <div class="pulse-ring"></div>
            <span class="banner-icon">🔔</span>
          </div>
          <div class="banner-text">
            <h3 class="banner-title">温馨提示</h3>
            <p class="banner-message">{{ trackingReminder.message }}</p>
          </div>
        </div>
        <button class="banner-action-btn" @click="gotoAssessment('scale')">
          立即测评
          <span class="action-arrow">→</span>
        </button>
      </div>

      <!-- 测评方式选择入口（核心功能区） -->
      <div class="assessment-entry">
        <div class="section-header">
          <div class="section-title-container">
            <div class="section-icon">📊</div>
            <h2 class="entry-title">选择测评方式</h2>
          </div>
          <p class="section-description">选择最适合您的方式进行心理健康评估</p>
        </div>

        <div class="entry-card-list">
          <div class="entry-card ai-card" @click="gotoConsultation">
            <div class="card-decoration">
              <div class="wave wave-1"></div>
              <div class="wave wave-2"></div>
            </div>
            <div class="card-content">
              <div class="card-icon-wrapper">
                <div class="card-icon">🩺</div>
              </div>
              <h3 class="card-title">AI 深度问诊</h3>
              <p class="card-desc">
                基于您的历史问卷测评结果，进行专业的AI深度心理咨询。支持针对同一份报告进行多次追踪问诊，获取更深层的建议。
              </p>
              <div class="card-features">
                <span class="feature-tag">🩺 深度解读</span>
                <span class="feature-tag">🔄 多次问诊</span>
              </div>
              <button class="card-action-btn">
                选择报告问诊
                <span class="action-arrow">→</span>
              </button>
            </div>
            <div class="card-corner">
              <div class="corner-icon">✨</div>
            </div>
          </div>

          <div class="entry-card scale-card" @click="gotoAssessment('scale')">
            <div class="card-decoration">
              <div class="dot-grid"></div>
            </div>
            <div class="card-content">
              <div class="card-icon-wrapper">
                <div class="card-icon">📋</div>
              </div>
              <h3 class="card-title">专业量表测评</h3>
              <p class="card-desc">使用经典心理量表，科学、快速地评估您的心理状态</p>
              <div class="card-features">
                <span class="feature-tag">📝 标准化</span>
                <span class="feature-tag">📈 可视化结果</span>
              </div>
              <button class="card-action-btn">
                开始测评
                <span class="action-arrow">→</span>
              </button>
            </div>
            <div class="card-corner">
              <div class="corner-icon">⭐</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 删除的三个功能卡片区域已移除 -->
    </main>

    <!-- 页脚 -->
    <footer class="home-footer">
      <div class="footer-content">
        <div class="footer-logo">
          <div class="footer-logo-icon">🌸</div>
          <div class="footer-logo-text">
            <h3>心灵驿站</h3>
            <p>Mental Harbor</p>
          </div>
        </div>
        <div class="footer-links">
          <a href="#" class="footer-link">关于我们</a>
          <a href="#" class="footer-link">隐私政策</a>
          <a href="#" class="footer-link">服务条款</a>
          <a href="#" class="footer-link">联系我们</a>
        </div>
        <div class="footer-social">
          <span class="social-icon">📱</span>
          <span class="social-icon">💬</span>
          <span class="social-icon">📧</span>
        </div>
      </div>
      <div class="footer-bottom">
        <p>心灵驿站 © 2025 版权所有 | 用心呵护每一颗心灵</p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { getHomeIndex } from '../api/home'
import type { HomeResponse } from '../api/home'

// 初始化路由和Pinia
const router = useRouter()
const authStore = useAuthStore()

// 响应式数据
const userInfo = ref({
  nickname: '',
  avatar_url: '',
})
const trackingReminder = ref({
  show: false,
  message: '',
})
const historyRecords = ref<HomeResponse['data']['history_records']>([])
const showUserMenu = ref(false)
const defaultAvatar =
  'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHZpZXdCb3g9IjAgMCA0MCA0MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iMjAiIGN5PSIyMCIgcj0iMjAiIGZpbGw9IiMwMDg5N0IiLz4KPHBhdGggZD0iTTIwIDI0QzIzLjMxMzcgMjQgMjYgMjEuMzEzNyAyNiAxOEMyNiAxNC42ODYzIDIzLjMxMzcgMTIgMjAgMTJDMTYuNjg2MyAxMiAxNCAxNC42ODYzIDE0IDE4QzE0IDIxLjMxMzcgMTYuNjg2MyAyNCAyMCAyNFoiIGZpbGw9IndoaXRlIi8+CjxjaXJjbGUgY3g9IjIwIiBjeT0iMTUiIHI9IjMiIGZpbGw9IndoaXRlIi8+Cjwvc3ZnPgo='

// 点击外部关闭用户菜单
const closeUserMenu = () => {
  showUserMenu.value = false
}

onMounted(async () => {
  // 添加全局点击事件监听
  document.addEventListener('click', closeUserMenu)

  if (!authStore.token || !localStorage.getItem('uid')) {
    router.push('/login')
    return
  }

  try {
    const uid = localStorage.getItem('uid')
    const response = await getHomeIndex(uid!)
    if (response.code === 200) {
      userInfo.value = response.data.user_info
      trackingReminder.value = response.data.tracking_reminder
      historyRecords.value = response.data.history_records
    }
  } catch (error) {
    console.error('首页数据加载失败:', error)
  }
})

onBeforeUnmount(() => {
  // 移除事件监听
  document.removeEventListener('click', closeUserMenu)
})

// 其他方法...
const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}

// 新增跳转到问诊选择页的方法
const gotoConsultation = () => {
  console.log('正在跳转到问诊选择页')
  // 这里跳转到我们刚刚新建的 ConsultationSelect 页面
  router.push('/consultation/select')
}

const gotoAssessment = (mode: string) => {
  // 打印日志方便调试
  console.log('正在跳转到测评页, 模式:', mode)

  // 核心跳转代码：确保路由路径 '/assessment' 与 router/index.ts 中定义的 path 一致
  router.push(`/assessment?mode=${mode}`)
}

// 导航方法
const gotoProfile = () => {
  router.push('/profile')
  showUserMenu.value = false
}

const gotoHistory = () => {
  console.log('跳转到历史档案') // 方便调试
  router.push('/history')
  showUserMenu.value = false // 跳转后关闭菜单
}

// 删除的三个功能相关方法已移除
</script>

<style scoped>
/* 全局样式 */

/* 页面容器 */
.home-container {
  /* --- 核心修改开始 --- */
  height: 100vh; /* 强制高度为屏幕高度 */
  overflow-y: auto; /* 允许竖向滚动 */
  overflow-x: hidden; /* 禁止横向滚动 */
  /* --- 核心修改结束 --- */

  width: 100%;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #f8f9ff 0%, #f0f7ff 50%, #e8f4ff 100%);
  position: relative;
}

/* 背景装饰元素 */
.background-decoration {
  position: fixed;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
}

.bubble {
  position: absolute;
  border-radius: 50%;
  background: rgba(0, 137, 123, 0.05);
  animation: float 20s infinite ease-in-out;
}

.bubble-1 {
  width: 300px;
  height: 300px;
  top: -150px;
  right: -100px;
}
.bubble-2 {
  width: 200px;
  height: 200px;
  bottom: 100px;
  left: -50px;
  animation-delay: -5s;
}
.bubble-3 {
  width: 150px;
  height: 150px;
  top: 30%;
  right: 20%;
  animation-delay: -10s;
}
.bubble-4 {
  width: 100px;
  height: 100px;
  bottom: 30%;
  left: 20%;
  animation-delay: -15s;
}

.leaf {
  position: absolute;
  font-size: 24px;
  opacity: 0.3;
  animation: sway 15s infinite ease-in-out;
}

.leaf-1 {
  top: 10%;
  left: 5%;
  animation-delay: -2s;
}
.leaf-2 {
  top: 60%;
  right: 8%;
  animation-delay: -8s;
}
.leaf-3 {
  bottom: 20%;
  left: 15%;
  animation-delay: -12s;
}

@keyframes float {
  0%,
  100% {
    transform: translateY(0) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(180deg);
  }
}

@keyframes sway {
  0%,
  100% {
    transform: rotate(-5deg);
  }
  50% {
    transform: rotate(5deg);
  }
}

/* 顶部导航栏 - 修复缩放问题 */
.home-header {
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(0, 137, 123, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
  width: 100%;
  min-height: 70px;
  padding: 0;
}

.header-container {
  width: 100%;
  max-width: 100%;
  margin: 0 auto;
  padding: 12px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
  flex-wrap: nowrap;
  min-width: 0;
}

/* 左侧logo区域 */
.header-left {
  display: flex;
  align-items: center;
  flex-shrink: 0;
  min-width: 0;
  margin-left: 10px;
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.logo-icon {
  font-size: 28px;
  animation: gentlePulse 4s infinite ease-in-out;
  flex-shrink: 0;
}

.logo-text-container {
  display: flex;
  flex-direction: column;
}

.logo-text {
  color: #00897b;
  font-size: 24px;
  margin: 0;
  font-weight: 700;
  background: linear-gradient(135deg, #00897b, #00acc1);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  white-space: nowrap;
  flex-shrink: 0;
  line-height: 1;
}

.logo-subtitle {
  font-size: 12px;
  color: #90a4ae;
  margin-top: 2px;
  letter-spacing: 1px;
  white-space: nowrap;
  flex-shrink: 0;
}

@keyframes gentlePulse {
  0%,
  100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

/* 右侧用户区域 - 修复缩放问题 */
.header-right {
  display: flex;
  align-items: center;
  position: relative;
  flex-shrink: 0;
  min-width: 0;
  /* 移除max-width限制，让容器可以自然扩展 */
  max-width: none;
  /* 使用自动布局而不是固定外边距 */
  margin-left: auto;
  margin-right: 20px;
}

.user-info-area {
  display: flex;
  align-items: center;
  gap: 15px;
  position: relative;
  /* 允许用户信息区域在需要时换行 */
  flex-wrap: nowrap;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 12px;
  border-radius: 12px;
  background: rgba(0, 137, 123, 0.05);
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  flex-shrink: 0;
  min-width: 0;
  /* 移除最大宽度限制，使用min-width确保最小可见性 */
  max-width: none;
  min-width: 160px;
}

.user-info:hover {
  background: rgba(0, 137, 123, 0.1);
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #00897b;
  box-shadow: 0 4px 12px rgba(0, 137, 123, 0.2);
  flex-shrink: 0;
}

.user-details {
  display: flex;
  flex-direction: column;
  min-width: 0;
  /* 允许用户信息区域在空间不足时收缩 */
  flex: 1;
}

.nickname {
  color: #263238;
  font-weight: 600;
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  /* 使用min-width而不是max-width */
  min-width: 60px;
}

.user-status {
  font-size: 11px;
  color: #4caf50;
  display: flex;
  align-items: center;
  gap: 4px;
  white-space: nowrap;
}

.status-dot {
  width: 6px;
  height: 6px;
  background: #4caf50;
  border-radius: 50%;
  display: inline-block;
}

.dropdown-arrow {
  font-size: 10px;
  color: #90a4ae;
  transition: transform 0.3s ease;
  flex-shrink: 0;
}

.rotate-180 {
  transform: rotate(180deg);
}

/* 用户菜单 */
.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.3s ease;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.user-menu {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 200px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  border: 1px solid rgba(0, 137, 123, 0.1);
  overflow: hidden;
  z-index: 1001;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  color: #546e7a;
  cursor: pointer;
  transition: all 0.2s ease;
}

.menu-item:hover {
  background: rgba(0, 137, 123, 0.05);
  color: #00897b;
}

.menu-icon {
  font-size: 16px;
}

.menu-divider {
  height: 1px;
  background: rgba(0, 0, 0, 0.1);
  margin: 4px 0;
}

.logout-item {
  color: #f44336;
}

.logout-item:hover {
  background: rgba(244, 67, 54, 0.05);
  color: #f44336;
}

/* 退出按钮 - 修复缩放问题 */
.logout-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: linear-gradient(135deg, #00897b, #00acc1);
  color: white;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(0, 137, 123, 0.3);
  position: relative;
  overflow: hidden;
  z-index: 1;
  flex-shrink: 0;
  white-space: nowrap;
  /* 使用min-width确保按钮始终可见 */
  min-width: 80px;
  /* 移除所有可能影响显示的max-width限制 */
  max-width: none;
}

.logout-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
  z-index: -1;
}

.logout-btn:hover::before {
  left: 100%;
}

.logout-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 137, 123, 0.4);
}

.btn-icon {
  font-size: 14px;
  flex-shrink: 0;
}

.btn-text {
  font-size: 14px;
  flex-shrink: 0;
}

/* 核心内容区 */
.home-main {
  flex: 1;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 25px;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  position: relative;
  z-index: 1;
  box-sizing: border-box;
}

/* 欢迎语区域 */
.welcome-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(240, 247, 255, 0.95));
  border-radius: 18px;
  padding: 25px;
  margin-bottom: 15px;
  border: 1px solid rgba(0, 137, 123, 0.1);
  box-shadow: 0 8px 25px rgba(0, 137, 123, 0.08);
  backdrop-filter: blur(10px);
  flex-wrap: wrap;
  width: 100%;
}

.welcome-content {
  flex: 1;
  min-width: 0;
}

.welcome-title {
  font-size: 26px;
  color: #263238;
  margin: 0 0 10px 0;
  font-weight: 700;
  line-height: 1.3;
}

.highlight {
  color: #00897b;
  position: relative;
  display: inline-block;
}

.highlight::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 6px;
  background: rgba(0, 137, 123, 0.2);
  z-index: -1;
  border-radius: 3px;
}

.welcome-subtitle {
  color: #90a4ae;
  font-size: 15px;
  margin: 0;
  line-height: 1.5;
}

.welcome-decoration {
  flex-shrink: 0;
  margin-left: 20px;
}

.quote-box {
  background: rgba(0, 137, 123, 0.1);
  border-radius: 12px;
  padding: 15px;
  text-align: center;
  min-width: 180px;
}

.quote-icon {
  font-size: 22px;
  margin-bottom: 8px;
}

.quote-text {
  color: #546e7a;
  font-size: 13px;
  font-style: italic;
  margin: 0;
  line-height: 1.4;
}

/* 复测提醒Banner */
.tracking-banner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
  border-radius: 16px;
  padding: 18px 25px;
  border: 1px solid #a5d6a7;
  animation: gentleGlow 3s infinite ease-in-out;
  flex-wrap: wrap;
  gap: 15px;
  width: 100%;
}

@keyframes gentleGlow {
  0%,
  100% {
    box-shadow: 0 4px 15px rgba(67, 160, 71, 0.1);
  }
  50% {
    box-shadow: 0 4px 15px rgba(67, 160, 71, 0.2);
  }
}

.banner-content {
  display: flex;
  align-items: center;
  gap: 18px;
  flex: 1;
  min-width: 0;
}

.banner-icon-wrapper {
  position: relative;
  flex-shrink: 0;
}

.pulse-ring {
  position: absolute;
  top: -8px;
  left: -8px;
  width: 52px;
  height: 52px;
  border: 2px solid #43a047;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  100% {
    transform: scale(1.5);
    opacity: 0;
  }
}

.banner-icon {
  font-size: 36px;
  position: relative;
  z-index: 1;
}

.banner-text {
  flex: 1;
  min-width: 0;
}

.banner-title {
  color: #2e7d32;
  font-size: 17px;
  margin: 0 0 5px 0;
  font-weight: 600;
}

.banner-message {
  color: #388e3c;
  margin: 0;
  font-size: 14px;
  line-height: 1.4;
}

.banner-action-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: #43a047;
  color: white;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 600;
  white-space: nowrap;
  flex-shrink: 0;
}

.banner-action-btn:hover {
  background: #388e3c;
  transform: translateX(5px);
}

.action-arrow {
  transition: transform 0.3s ease;
}

.banner-action-btn:hover .action-arrow {
  transform: translateX(3px);
}

/* 测评入口区域 */
.section-header {
  margin-bottom: 25px;
  width: 100%;
}

.section-title-container {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.section-icon {
  font-size: 22px;
}

.entry-title,
.history-title {
  color: #263238;
  font-size: 22px;
  margin: 0;
  font-weight: 700;
}

.section-description {
  color: #90a4ae;
  font-size: 14px;
  margin: 0;
  padding-left: 34px;
}

.entry-card-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 25px;
  width: 100%;
}

.entry-card {
  background: white;
  border-radius: 18px;
  padding: 25px;
  position: relative;
  overflow: hidden;
  transition: all 0.4s ease;
  border: 1px solid rgba(0, 137, 123, 0.1);
  cursor: pointer;
  min-height: 280px;
  display: flex;
  flex-direction: column;
  width: 100%;
  box-sizing: border-box;
}

.entry-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 15px 35px rgba(0, 137, 123, 0.15);
}

.ai-card {
  background: linear-gradient(135deg, #f8fdff, #e3f2fd);
}

.scale-card {
  background: linear-gradient(135deg, #f9f8ff, #ede7f6);
}

.card-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  overflow: hidden;
}

.wave {
  position: absolute;
  height: 150%;
  width: 200%;
  background: rgba(0, 137, 123, 0.03);
  border-radius: 40%;
  animation: wave 15s infinite linear;
}

.wave-1 {
  top: -30%;
  left: -50%;
  animation-delay: 0s;
}

.wave-2 {
  top: -20%;
  left: -60%;
  animation-delay: -5s;
}

.dot-grid {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: radial-gradient(rgba(0, 137, 123, 0.1) 1px, transparent 1px);
  background-size: 20px 20px;
  opacity: 0.5;
}

@keyframes wave {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.card-content {
  position: relative;
  z-index: 1;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.card-icon-wrapper {
  margin-bottom: 18px;
}

.card-icon {
  font-size: 44px;
  display: inline-block;
  animation: gentleFloat 4s infinite ease-in-out;
}

@keyframes gentleFloat {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-8px);
  }
}

.card-title {
  color: #00897b;
  font-size: 20px;
  margin: 0 0 12px 0;
  font-weight: 700;
}

.card-desc {
  color: #546e7a;
  font-size: 14px;
  line-height: 1.5;
  margin: 0 0 18px 0;
  flex: 1;
}

.card-features {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.feature-tag {
  padding: 6px 12px;
  background: rgba(0, 137, 123, 0.1);
  border-radius: 8px;
  font-size: 12px;
  color: #00897b;
  white-space: nowrap;
}

.card-action-btn {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  background: linear-gradient(135deg, #00897b, #00acc1);
  color: white;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  margin-top: auto;
  width: 100%;
  box-sizing: border-box;
}

.card-action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(0, 137, 123, 0.3);
}

.card-corner {
  position: absolute;
  top: 20px;
  right: 20px;
}

.corner-icon {
  font-size: 22px;
  opacity: 0.3;
}

/* 历史记录区域 */
.history-section {
  margin-top: 20px;
  width: 100%;
}

.history-list {
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 25px rgba(0, 137, 123, 0.08);
  overflow: hidden;
  width: 100%;
}

.history-item {
  display: flex;
  align-items: center;
  padding: 18px 25px;
  border-bottom: 1px solid rgba(0, 137, 123, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  flex-wrap: wrap;
  width: 100%;
  box-sizing: border-box;
}

.history-item:hover {
  background: rgba(0, 137, 123, 0.03);
  transform: translateX(5px);
}

.history-item:last-child {
  border-bottom: none;
}

.item-decoration {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  transition: width 0.3s ease;
}

.history-item:hover .item-decoration {
  width: 8px;
}

.item-decoration.mild {
  background: #43a047;
}
.item-decoration.moderate {
  background: #ffb300;
}
.item-decoration.severe {
  background: #e53935;
}

.item-left,
.item-center,
.item-right {
  flex: 1;
  min-width: 0;
  margin-bottom: 10px;
}

.item-left {
  min-width: 120px;
  max-width: 150px;
}

.item-center {
  padding: 0 15px;
  flex: 2;
}

.item-right {
  text-align: right;
  min-width: 120px;
  max-width: 150px;
}

.record-date {
  color: #546e7a;
  font-size: 14px;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.date-icon {
  font-size: 14px;
}

.mode-tag {
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 12px;
  color: white;
  display: inline-block;
  white-space: nowrap;
}

.mode-tag.ai_chat {
  background: linear-gradient(135deg, #00897b, #00acc1);
}

.mode-tag.scale {
  background: linear-gradient(135deg, #8e24aa, #ab47bc);
}

.record-summary {
  color: #263238;
  font-weight: 600;
  font-size: 15px;
  margin-bottom: 8px;
  line-height: 1.3;
}

.record-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.duration-tag,
.accuracy-tag {
  padding: 4px 8px;
  background: rgba(0, 137, 123, 0.05);
  border-radius: 6px;
  font-size: 11px;
  color: #00897b;
  white-space: nowrap;
}

.risk-indicator {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  margin-bottom: 8px;
}

.risk-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.risk-indicator.mild .risk-dot {
  background: #43a047;
}
.risk-indicator.moderate .risk-dot {
  background: #ffb300;
}
.risk-indicator.severe .risk-dot {
  background: #e53935;
}

.risk-text {
  font-size: 14px;
  font-weight: 600;
}

.risk-indicator.mild .risk-text {
  color: #43a047;
}
.risk-indicator.moderate .risk-text {
  color: #ffb300;
}
.risk-indicator.severe .risk-text {
  color: #e53935;
}

.view-detail {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: #00897b;
  font-size: 12px;
  font-weight: 600;
  transition: gap 0.3s ease;
  white-space: nowrap;
}

.history-item:hover .view-detail {
  gap: 8px;
}

.view-arrow {
  transition: transform 0.3s ease;
}

.history-item:hover .view-arrow {
  transform: translateX(3px);
}

/* 页脚 */
.home-footer {
  background: linear-gradient(135deg, #263238, #37474f);
  color: white;
  margin-top: 50px;
  padding: 40px 0 20px;
  position: relative;
  width: 100%;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  flex-wrap: wrap;
  gap: 30px;
}

.footer-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.footer-logo-icon {
  font-size: 32px;
}

.footer-logo-text h3 {
  color: white;
  margin: 0 0 4px 0;
  font-size: 20px;
}

.footer-logo-text p {
  color: #cfd8dc;
  margin: 0;
  font-size: 12px;
}

.footer-links {
  display: flex;
  gap: 25px;
  flex-wrap: wrap;
}

.footer-link {
  color: #cfd8dc;
  text-decoration: none;
  font-size: 14px;
  transition: color 0.3s ease;
  white-space: nowrap;
}

.footer-link:hover {
  color: #00897b;
}

.footer-social {
  display: flex;
  gap: 15px;
}

.social-icon {
  font-size: 20px;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.social-icon:hover {
  transform: translateY(-3px);
  color: #00897b;
}

.footer-bottom {
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  width: 100%;
}

.footer-bottom p {
  margin: 0;
  color: #90a4ae;
  font-size: 14px;
}

/* ================================================ */
/* 修复缩放问题的关键CSS修改 */
/* ================================================ */

/* 1. 移除所有可能限制容器宽度的max-width */
.header-right {
  max-width: none !important;
}

.user-info {
  max-width: none !important;
}

.logout-btn {
  max-width: none !important;
}

/* 2. 使用min-width确保最小可见性 */
.user-info {
  min-width: 160px;
}

.logout-btn {
  min-width: 80px;
}

/* 3. 优化flex布局，确保元素不会被挤压 */
.user-info-area {
  flex-wrap: nowrap;
}

/* 4. 为关键元素添加flex-shrink: 0防止被压缩 */
.logout-btn,
.user-info,
.avatar {
  flex-shrink: 0;
}

/* 5. 添加专门针对100%缩放以下的媒体查询 */
@media screen and (max-width: 1400px) {
  .header-container {
    padding: 12px 15px;
  }

  /* 在中等屏幕下，适当调整用户信息区域 */
  .user-info {
    min-width: 140px;
    padding: 6px 10px;
  }

  .nickname {
    min-width: 50px;
    font-size: 13px;
  }

  .logout-btn {
    min-width: 70px;
    padding: 8px 14px;
  }

  .logo-text {
    font-size: 22px;
  }
}

/* 6. 修复缩放时可能触发的响应式断点问题 */
/* 修改原来的媒体查询，确保在缩放100%时不会触发不适当的样式 */

/* 原来的1024px媒体查询调整 */
@media (max-width: 1200px) {
  .header-container {
    padding: 10px 15px;
  }

  .logo-text {
    font-size: 22px;
  }

  .user-info {
    min-width: 130px;
    padding: 6px 10px;
  }

  .nickname {
    min-width: 45px;
    font-size: 13px;
  }

  .logout-btn {
    min-width: 65px;
    padding: 8px 12px;
  }

  .entry-card-list {
    grid-template-columns: 1fr;
  }

  .welcome-section {
    padding: 20px;
  }

  .welcome-title {
    font-size: 24px;
  }
}

/* 原来的768px媒体查询调整 */
@media (max-width: 900px) {
  .header-container {
    flex-wrap: wrap;
    gap: 10px;
  }

  .header-left,
  .header-right {
    width: 100%;
  }

  .header-right {
    justify-content: space-between;
    order: 3;
    margin-top: 10px;
    margin-right: 0;
  }

  .user-info-area {
    width: 100%;
    justify-content: space-between;
  }

  .user-info {
    flex: 1;
    max-width: none;
  }

  .logout-btn {
    position: static;
    order: 2;
  }

  .home-main {
    padding: 15px;
  }

  .welcome-section {
    flex-direction: column;
    text-align: center;
    padding: 20px;
  }

  .welcome-decoration {
    margin-left: 0;
    margin-top: 20px;
  }

  .tracking-banner {
    flex-direction: column;
    text-align: center;
    gap: 15px;
  }

  .banner-content {
    flex-direction: column;
    gap: 15px;
  }

  .entry-card {
    padding: 20px;
  }

  .history-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }

  .item-left,
  .item-center,
  .item-right {
    width: 100%;
    text-align: left;
    max-width: none;
    padding: 0;
  }

  .risk-indicator {
    justify-content: flex-start;
  }

  .footer-content {
    flex-direction: column;
    gap: 25px;
    text-align: center;
  }

  .footer-links {
    justify-content: center;
  }
}

/* 原来的480px媒体查询调整 */
@media (max-width: 600px) {
  .logo-text {
    font-size: 20px;
  }

  .logo-subtitle {
    display: none;
  }

  /* 在小屏幕下，退出按钮只显示图标 */
  .logout-btn .btn-text {
    display: none;
  }

  .logout-btn {
    padding: 8px 10px;
    min-width: 40px;
    justify-content: center;
  }

  .nickname {
    min-width: 40px;
    font-size: 12px;
  }

  .user-status {
    font-size: 10px;
  }

  .user-info {
    min-width: 120px;
  }

  .welcome-title {
    font-size: 22px;
  }

  .entry-title,
  .history-title {
    font-size: 20px;
  }

  .section-description {
    padding-left: 0;
  }

  .entry-card-list {
    gap: 15px;
  }

  .card-title {
    font-size: 18px;
  }

  .card-desc {
    font-size: 13px;
  }

  .history-item {
    padding: 15px;
  }
}

/* 7. 特别针对缩放问题的修复 */
/* 确保在缩放100%及以下时，导航栏有足够的空间 */
@media screen and (min-width: 1200px) and (max-width: 1600px) {
  /* 这是常见的桌面屏幕范围，确保在这个范围内布局正常 */
  .header-container {
    padding: 12px 30px;
  }

  .header-right {
    margin-right: 30px;
  }
}

/* 8. 防止水平滚动条出现 */
@media screen and (max-width: 1200px) {
  .home-container {
    overflow-x: hidden;
  }

  .background-decoration {
    width: 100vw;
  }
}

/* 9. 修复全屏显示的关键CSS */
@media screen and (min-width: 1201px) {
  .home-main {
    padding: 30px calc((100vw - 1200px) / 2);
  }

  .home-footer {
    padding-left: calc((100vw - 1200px) / 2);
    padding-right: calc((100vw - 1200px) / 2);
  }
}

/* 确保在全屏时背景框不被遮挡 */
@media screen and (min-width: 1400px) {
  .background-decoration {
    left: calc((100vw - 1400px) / 2);
    width: 1400px;
  }
}
</style>
