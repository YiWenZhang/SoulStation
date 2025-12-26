<template>
  <div class="page-wrapper">
    <!-- 动态背景 -->
    <div class="animated-bg">
      <div class="gradient-orb orb-1"></div>
      <div class="gradient-orb orb-2"></div>
      <div class="gradient-orb orb-3"></div>
      <div class="floating-shapes">
        <div class="shape shape-1">✨</div>
        <div class="shape shape-2">🌿</div>
        <div class="shape shape-3">💫</div>
        <div class="shape shape-4">🍃</div>
      </div>
      <div class="grid-overlay"></div>
    </div>

    <div class="content-container">
      <!-- 顶部导航 -->
      <div class="top-nav">
        <button class="nav-back" @click="goHome">
          <span class="back-icon">←</span>
          <span class="back-text">返回首页</span>
        </button>
        <div class="nav-title">
          <span class="title-icon">👤</span>
          <span>个人中心</span>
        </div>
        <div class="nav-placeholder"></div>
      </div>

      <!-- 主卡片 -->
      <div class="profile-card">
        <div class="card-glow"></div>

        <div class="profile-layout">
          <!-- 左侧面板 -->
          <div class="left-panel">
            <div class="panel-bg">
              <div class="wave wave-1"></div>
              <div class="wave wave-2"></div>
              <div class="circle-deco circle-1"></div>
              <div class="circle-deco circle-2"></div>
            </div>

            <div class="panel-content">
              <!-- 头像区域 -->
              <div class="avatar-section">
                <el-upload
                  class="avatar-uploader"
                  action=""
                  :show-file-list="false"
                  :auto-upload="false"
                  :on-change="handleFileChange"
                >
                  <div class="avatar-wrapper">
                    <div class="avatar-ring">
                      <div class="ring-segment"></div>
                      <div class="ring-segment"></div>
                      <div class="ring-segment"></div>
                    </div>

                    <div class="avatar-inner">
                      <img
                        v-if="userInfo.avatar_url"
                        :src="userInfo.avatar_url"
                        class="avatar-img"
                      />
                      <div v-else class="avatar-placeholder">
                        {{ (userInfo.nickname || 'U').charAt(0).toUpperCase() }}
                      </div>
                    </div>

                    <div class="avatar-overlay">
                      <el-icon :size="28"><Camera /></el-icon>
                      <span class="upload-hint">点击更换</span>
                    </div>

                    <div class="avatar-badge">
                      <span>📸</span>
                    </div>
                  </div>
                </el-upload>

                <!-- 上传确认按钮 -->
                <Transition name="fade-slide">
                  <div v-if="selectedFile" class="upload-actions">
                    <button class="upload-confirm" @click="executeUpload" :disabled="uploading">
                      <span v-if="!uploading">✓ 确认上传</span>
                      <span v-else class="loading-dots"
                        >上传中<span>.</span><span>.</span><span>.</span></span
                      >
                    </button>
                    <button class="upload-cancel" @click="cancelUpload">取消</button>
                  </div>
                </Transition>
              </div>

              <!-- 用户信息 -->
              <div class="user-info">
                <h2 class="user-name">{{ userInfo.nickname || '未命名用户' }}</h2>
                <div class="user-role">
                  <span class="role-icon">⭐</span>
                  <span class="role-text">正式会员</span>
                </div>
                <div class="user-meta">
                  <div class="meta-item">
                    <span class="meta-icon">📅</span>
                    <span>加入于 2025年</span>
                  </div>
                  <div class="meta-item">
                    <span class="meta-icon">📱</span>
                    <span>{{ userInfo.phone }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 右侧面板 -->
          <div class="right-panel">
            <div class="form-section">
              <div class="section-header">
                <div class="header-icon">✏️</div>
                <div class="header-text">
                  <h3>编辑个人资料</h3>
                  <p>完善信息，让大家更好地认识你</p>
                </div>
              </div>

              <div class="form-body">
                <!-- 昵称输入 -->
                <div class="form-group">
                  <label class="form-label">
                    <span class="label-icon">👤</span>
                    <span>昵称</span>
                  </label>
                  <div class="input-wrapper">
                    <el-input
                      v-model="form.nickname"
                      placeholder="请输入您的昵称"
                      class="custom-input"
                      size="large"
                    >
                      <template #prefix>
                        <el-icon><User /></el-icon>
                      </template>
                    </el-input>
                    <div class="input-hint">2-20个字符，支持中英文和数字</div>
                  </div>
                </div>

                <!-- 手机号 -->
                <div class="form-group">
                  <label class="form-label">
                    <span class="label-icon">📱</span>
                    <span>手机号码</span>
                    <span class="label-badge">已绑定</span>
                  </label>
                  <div class="input-wrapper">
                    <el-input
                      v-model="userInfo.phone"
                      disabled
                      class="custom-input disabled"
                      size="large"
                    >
                      <template #prefix>
                        <el-icon><Iphone /></el-icon>
                      </template>
                      <template #suffix>
                        <el-icon class="lock-icon"><Lock /></el-icon>
                      </template>
                    </el-input>
                    <div class="input-hint">手机号作为登录凭证，暂不支持修改</div>
                  </div>
                </div>
              </div>

              <!-- 操作按钮 -->
              <div class="form-actions">
                <button class="btn-secondary" @click="goHome">
                  <span class="btn-icon">←</span>
                  <span>返回</span>
                </button>
                <button class="btn-primary" @click="handleSaveProfile" :disabled="saving">
                  <span v-if="!saving" class="btn-content">
                    <span class="btn-icon">💾</span>
                    <span>保存修改</span>
                  </span>
                  <span v-else class="btn-loading">
                    <span class="spinner"></span>
                    <span>保存中...</span>
                  </span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 底部版权 -->
      <div class="footer-info">
        <span>🌿 心理健康平台 · 守护您的心灵</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { UploadFile } from 'element-plus'
import { Camera, User, Iphone, Lock } from '@element-plus/icons-vue'
import { updateProfile, uploadAvatar } from '@/api/user'
import { useAuthStore } from '@/stores/auth'

interface UserInfo {
  uid: string | null
  nickname: string
  avatar_url: string
  phone: string
}

const router = useRouter()
const authStore = useAuthStore()

const userInfo = ref<UserInfo>({
  uid: null,
  nickname: '',
  avatar_url: '',
  phone: '',
})

const form = reactive({
  nickname: '',
})

const selectedFile = ref<File | null>(null)
const oldAvatarUrl = ref('')
const uploading = ref(false)
const saving = ref(false)

const goHome = () => {
  router.push('/home')
}

onMounted(() => {
  const storedAvatar = localStorage.getItem('avatar_url') || ''

  userInfo.value = {
    uid: localStorage.getItem('uid'),
    nickname: localStorage.getItem('nickname') || '',
    avatar_url: storedAvatar,
    phone: '138****8888',
  }
  form.nickname = userInfo.value.nickname
  oldAvatarUrl.value = storedAvatar
})

const handleFileChange = (file: UploadFile) => {
  if (!file.raw) return

  const isImg = ['image/jpeg', 'image/png', 'image/gif'].includes(file.raw.type)
  const isLt2M = file.raw.size / 1024 / 1024 < 2

  if (!isImg) {
    ElMessage.error('请上传 JPG/PNG/GIF 格式的图片')
    return
  }
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB')
    return
  }

  userInfo.value.avatar_url = URL.createObjectURL(file.raw)
  selectedFile.value = file.raw
}

const cancelUpload = () => {
  selectedFile.value = null
  userInfo.value.avatar_url = oldAvatarUrl.value
}

const executeUpload = async () => {
  if (!selectedFile.value || !userInfo.value.uid) return

  uploading.value = true
  try {
    const res = await uploadAvatar(userInfo.value.uid, selectedFile.value)
    if (res.code === 200) {
      ElMessage.success('头像更新成功')
      const newUrl = res.data.avatar_url

      localStorage.setItem('avatar_url', newUrl)
      userInfo.value.avatar_url = newUrl
      oldAvatarUrl.value = newUrl
      selectedFile.value = null

      if (authStore.user) {
        authStore.user.avatar_url = newUrl
      }
    }
  } catch (err) {
    console.error(err)
    ElMessage.error('上传失败，请重试')
  } finally {
    uploading.value = false
  }
}

const handleSaveProfile = async () => {
  if (!form.nickname.trim()) {
    ElMessage.warning('昵称不能为空')
    return
  }

  if (!userInfo.value.uid) {
    ElMessage.error('登录状态失效，请重新登录')
    router.push('/login')
    return
  }

  saving.value = true
  try {
    const res = await updateProfile(userInfo.value.uid, form.nickname)
    if (res.code === 200) {
      ElMessage.success('个人资料已保存')
      localStorage.setItem('nickname', form.nickname)
      userInfo.value.nickname = form.nickname

      if (authStore.user) {
        authStore.user.nickname = form.nickname
      }
    } else {
      ElMessage.error(res.msg || '保存失败')
    }
  } catch (err) {
    console.error(err)
    ElMessage.error('网络错误，请稍后重试')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
/* ============ 页面容器与背景 ============ */
.page-wrapper {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8f5e9 50%, #e3f2fd 100%);
  position: relative;
  overflow: hidden;
  padding: 20px;
}

/* 动态背景 */
.animated-bg {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}

.gradient-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.5;
  animation: floatOrb 20s ease-in-out infinite;
}

.orb-1 {
  width: 400px;
  height: 400px;
  background: linear-gradient(135deg, #a5d6a7 0%, #81d4fa 100%);
  top: -100px;
  right: -100px;
}

.orb-2 {
  width: 300px;
  height: 300px;
  background: linear-gradient(135deg, #c5e1a5 0%, #b2dfdb 100%);
  bottom: 10%;
  left: -80px;
  animation-delay: -7s;
}

.orb-3 {
  width: 250px;
  height: 250px;
  background: linear-gradient(135deg, #b2ebf2 0%, #c8e6c9 100%);
  top: 40%;
  right: 10%;
  animation-delay: -14s;
}

@keyframes floatOrb {
  0%,
  100% {
    transform: translate(0, 0) scale(1);
  }
  25% {
    transform: translate(30px, -30px) scale(1.05);
  }
  50% {
    transform: translate(-20px, 20px) scale(0.95);
  }
  75% {
    transform: translate(20px, 30px) scale(1.02);
  }
}

.floating-shapes {
  position: absolute;
  inset: 0;
}

.shape {
  position: absolute;
  font-size: 24px;
  opacity: 0.4;
  animation: shapeFloat 15s ease-in-out infinite;
}

.shape-1 {
  top: 10%;
  left: 5%;
  animation-delay: 0s;
}
.shape-2 {
  top: 20%;
  right: 10%;
  animation-delay: -3s;
}
.shape-3 {
  bottom: 30%;
  left: 8%;
  animation-delay: -6s;
}
.shape-4 {
  bottom: 15%;
  right: 15%;
  animation-delay: -9s;
}

@keyframes shapeFloat {
  0%,
  100% {
    transform: translateY(0) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(10deg);
  }
}

.grid-overlay {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(0, 0, 0, 0.015) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 0, 0, 0.015) 1px, transparent 1px);
  background-size: 50px 50px;
}

/* ============ 内容容器 ============ */
.content-container {
  max-width: 1000px;
  margin: 0 auto;
  position: relative;
  z-index: 1;
}

/* ============ 顶部导航 ============ */
.top-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0 20px;
  margin-bottom: 10px;
}

.nav-back {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 25px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  color: #546e7a;
}

.nav-back:hover {
  background: white;
  transform: translateX(-3px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
}

.back-icon {
  font-size: 18px;
  transition: transform 0.3s;
}

.nav-back:hover .back-icon {
  transform: translateX(-3px);
}

.nav-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #37474f;
}

.title-icon {
  font-size: 22px;
}

.nav-placeholder {
  width: 100px;
}

/* ============ 主卡片 ============ */
.profile-card {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 28px;
  overflow: hidden;
  box-shadow:
    0 25px 50px rgba(0, 0, 0, 0.08),
    0 0 0 1px rgba(255, 255, 255, 0.5);
  position: relative;
  animation: cardAppear 0.8s ease-out;
}

@keyframes cardAppear {
  from {
    opacity: 0;
    transform: translateY(40px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.card-glow {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle at 30% 30%, rgba(129, 199, 132, 0.1) 0%, transparent 50%);
  pointer-events: none;
}

.profile-layout {
  display: flex;
  min-height: 520px;
}

/* ============ 左侧面板 ============ */
.left-panel {
  width: 320px;
  flex-shrink: 0;
  background: linear-gradient(160deg, #66bb6a 0%, #26a69a 50%, #42a5f5 100%);
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.panel-bg {
  position: absolute;
  inset: 0;
  overflow: hidden;
}

.wave {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 200%;
  height: 200px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 40%;
  animation: wave 15s linear infinite;
}

.wave-1 {
  bottom: -80px;
  animation-duration: 15s;
}

.wave-2 {
  bottom: -100px;
  animation-duration: 20s;
  animation-direction: reverse;
  opacity: 0.5;
}

@keyframes wave {
  0% {
    transform: translateX(0) rotate(0deg);
  }
  100% {
    transform: translateX(-50%) rotate(360deg);
  }
}

.circle-deco {
  position: absolute;
  border: 2px solid rgba(255, 255, 255, 0.15);
  border-radius: 50%;
}

.circle-1 {
  width: 180px;
  height: 180px;
  top: -40px;
  right: -40px;
}

.circle-2 {
  width: 120px;
  height: 120px;
  bottom: 20%;
  left: -30px;
}

.panel-content {
  position: relative;
  z-index: 2;
  text-align: center;
  padding: 40px 30px;
  color: white;
}

/* 头像区域 */
.avatar-section {
  margin-bottom: 30px;
}

.avatar-wrapper {
  width: 130px;
  height: 130px;
  margin: 0 auto;
  position: relative;
  cursor: pointer;
}

.avatar-ring {
  position: absolute;
  inset: -6px;
  border-radius: 50%;
  overflow: hidden;
}

.ring-segment {
  position: absolute;
  inset: 0;
  border: 3px solid transparent;
  border-top-color: rgba(255, 255, 255, 0.8);
  border-radius: 50%;
  animation: ringRotate 3s linear infinite;
}

.ring-segment:nth-child(2) {
  animation-delay: -1s;
  border-top-color: rgba(255, 255, 255, 0.5);
}

.ring-segment:nth-child(3) {
  animation-delay: -2s;
  border-top-color: rgba(255, 255, 255, 0.3);
}

@keyframes ringRotate {
  to {
    transform: rotate(360deg);
  }
}

.avatar-inner {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: white;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
  transition: transform 0.3s ease;
}

.avatar-wrapper:hover .avatar-inner {
  transform: scale(1.05);
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  font-size: 52px;
  font-weight: 700;
  background: linear-gradient(135deg, #66bb6a, #42a5f5);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.avatar-overlay {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
  color: white;
}

.avatar-wrapper:hover .avatar-overlay {
  opacity: 1;
}

.upload-hint {
  font-size: 12px;
  margin-top: 4px;
}

.avatar-badge {
  position: absolute;
  bottom: 5px;
  right: 5px;
  width: 32px;
  height: 32px;
  background: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  font-size: 16px;
  transition: transform 0.3s;
}

.avatar-wrapper:hover .avatar-badge {
  transform: scale(1.1) rotate(10deg);
}

/* 上传操作按钮 */
.upload-actions {
  margin-top: 16px;
  display: flex;
  gap: 10px;
  justify-content: center;
}

.upload-confirm {
  padding: 8px 20px;
  background: white;
  color: #43a047;
  border: none;
  border-radius: 20px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 14px;
}

.upload-confirm:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.upload-confirm:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.upload-cancel {
  padding: 8px 16px;
  background: transparent;
  color: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.4);
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 14px;
}

.upload-cancel:hover {
  background: rgba(255, 255, 255, 0.1);
}

.loading-dots span {
  animation: dotBlink 1.4s infinite;
}
.loading-dots span:nth-child(2) {
  animation-delay: 0.2s;
}
.loading-dots span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes dotBlink {
  0%,
  100% {
    opacity: 0.2;
  }
  50% {
    opacity: 1;
  }
}

/* 用户信息 */
.user-info {
  margin-bottom: 20px;
}

.user-name {
  font-size: 26px;
  font-weight: 700;
  margin: 0 0 12px;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.user-role {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 16px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 15px;
}

.user-meta {
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: 13px;
  opacity: 0.9;
}

.meta-item {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

/* ============ 右侧面板 ============ */
.right-panel {
  flex: 1;
  padding: 40px;
  display: flex;
  flex-direction: column;
}

.form-section {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.section-header {
  display: flex;
  align-items: flex-start;
  gap: 15px;
  margin-bottom: 35px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.header-icon {
  font-size: 32px;
  line-height: 1;
}

.header-text h3 {
  font-size: 22px;
  font-weight: 600;
  color: #263238;
  margin: 0 0 6px;
}

.header-text p {
  font-size: 14px;
  color: #78909c;
  margin: 0;
}

/* 表单样式 */
.form-body {
  flex: 1;
}

.form-group {
  margin-bottom: 28px;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
  font-size: 15px;
  font-weight: 500;
  color: #37474f;
}

.label-icon {
  font-size: 16px;
}

.label-badge {
  font-size: 11px;
  padding: 2px 8px;
  background: linear-gradient(135deg, #c8e6c9, #b2dfdb);
  color: #2e7d32;
  border-radius: 10px;
  font-weight: 600;
}

.input-wrapper {
  position: relative;
}

:deep(.custom-input .el-input__wrapper) {
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  border: 2px solid #e8f5e9;
  transition: all 0.3s ease;
  padding: 4px 12px;
}

:deep(.custom-input .el-input__wrapper:hover) {
  border-color: #a5d6a7;
}

:deep(.custom-input .el-input__wrapper.is-focus) {
  border-color: #66bb6a;
  box-shadow: 0 0 0 4px rgba(102, 187, 106, 0.1);
}

:deep(.custom-input.disabled .el-input__wrapper) {
  background: #f5f5f5;
  border-color: #e0e0e0;
}

.lock-icon {
  color: #bdbdbd;
}

.input-hint {
  font-size: 12px;
  color: #9e9e9e;
  margin-top: 8px;
  padding-left: 4px;
}

/* 操作按钮 */
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  margin-top: auto;
  padding-top: 30px;
  border-top: 1px solid #f0f0f0;
}

.btn-secondary {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: #f5f5f5;
  color: #546e7a;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-secondary:hover {
  background: #eeeeee;
  transform: translateX(-3px);
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 28px;
  background: linear-gradient(135deg, #66bb6a 0%, #26a69a 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 187, 106, 0.3);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 187, 106, 0.4);
}

.btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-loading {
  display: flex;
  align-items: center;
  gap: 10px;
}

.spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* ============ 底部版权 ============ */
.footer-info {
  text-align: center;
  padding: 25px 0 10px;
  font-size: 13px;
  color: #90a4ae;
}

/* ============ 过渡动画 ============ */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* ============ 响应式 ============ */
@media (max-width: 768px) {
  .page-wrapper {
    padding: 15px;
  }

  .top-nav {
    padding: 5px 0 15px;
  }

  .back-text {
    display: none;
  }

  .nav-title {
    font-size: 16px;
  }

  .profile-layout {
    flex-direction: column;
    min-height: auto;
  }

  .left-panel {
    width: 100%;
    padding: 30px 20px;
  }

  .panel-content {
    padding: 20px;
  }

  .avatar-wrapper {
    width: 100px;
    height: 100px;
  }

  .avatar-placeholder {
    font-size: 40px;
  }

  .user-name {
    font-size: 22px;
  }

  .right-panel {
    padding: 25px 20px;
  }

  .section-header {
    margin-bottom: 25px;
    padding-bottom: 15px;
  }

  .header-text h3 {
    font-size: 18px;
  }

  .form-actions {
    flex-direction: column-reverse;
  }

  .btn-secondary,
  .btn-primary {
    width: 100%;
    justify-content: center;
  }
}
</style>
