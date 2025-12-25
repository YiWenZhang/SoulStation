<template>
  <div class="page-wrapper">
    <div class="bg-shape"></div>

    <div class="content-container">
      <el-card class="profile-card" :body-style="{ padding: '0px' }">
        <el-row class="profile-layout">
          <el-col :xs="24" :sm="8" class="left-panel">
            <div class="panel-content">
              <div class="avatar-container">
                <el-upload
                  class="avatar-uploader"
                  action=""
                  :show-file-list="false"
                  :auto-upload="false"
                  :on-change="handleFileChange"
                >
                  <div class="avatar-wrapper">
                    <img v-if="userInfo.avatar_url" :src="userInfo.avatar_url" class="avatar-img" />
                    <div v-else class="avatar-placeholder">
                      {{ (userInfo.nickname || 'User').charAt(0).toUpperCase() }}
                    </div>

                    <div class="avatar-overlay">
                      <el-icon :size="24"><Camera /></el-icon>
                      <span class="upload-text">更换头像</span>
                    </div>
                  </div>
                </el-upload>

                <div v-if="selectedFile" class="upload-actions">
                  <el-button
                    type="success"
                    size="small"
                    round
                    @click="executeUpload"
                    :loading="uploading"
                  >
                    确认上传
                  </el-button>
                  <el-button link size="small" class="cancel-btn" @click="cancelUpload">
                    取消
                  </el-button>
                </div>
              </div>

              <div class="user-identity">
                <h2 class="display-name">{{ userInfo.nickname || '未命名用户' }}</h2>
                <el-tag effect="dark" round type="success" class="role-tag"> 正式会员 </el-tag>
                <div class="join-date">加入于 2025年</div>
              </div>
            </div>

            <div class="circle-deco"></div>
          </el-col>

          <el-col :xs="24" :sm="16" class="right-panel">
            <div class="form-header">
              <h3>编辑个人资料</h3>
              <p class="subtitle">完善信息，让大家更好地认识你</p>
            </div>

            <el-form label-position="top" class="edit-form" size="large">
              <el-form-item label="昵称">
                <el-input
                  v-model="form.nickname"
                  placeholder="请输入您的昵称"
                  :prefix-icon="User"
                />
              </el-form-item>

              <el-form-item label="手机号码">
                <el-input v-model="userInfo.phone" disabled :prefix-icon="Iphone">
                  <template #append>
                    <el-icon><Lock /></el-icon>
                  </template>
                </el-input>
                <span class="form-tip">手机号作为登录凭证，暂不支持直接修改</span>
              </el-form-item>

              <div class="action-footer">
                <el-button class="back-btn" @click="goHome">返回首页</el-button>
                <el-button
                  type="primary"
                  @click="handleSaveProfile"
                  :loading="saving"
                  class="save-btn"
                >
                  保存修改
                </el-button>
              </div>
            </el-form>
          </el-col>
        </el-row>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { UploadFile } from 'element-plus'
// 引入图标
import { Camera, User, Iphone, Lock } from '@element-plus/icons-vue'
import { updateProfile, uploadAvatar } from '@/api/user'
import { useAuthStore } from '@/stores/auth'

// 定义接口
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
// 备份旧头像URL，用于取消上传时恢复
const oldAvatarUrl = ref('')
const uploading = ref(false)
const saving = ref(false)

const goHome = () => {
  router.push('/home')
}

onMounted(() => {
  // 从 LocalStorage 或 Store 初始化
  const storedAvatar = localStorage.getItem('avatar_url') || ''

  userInfo.value = {
    uid: localStorage.getItem('uid'),
    nickname: localStorage.getItem('nickname') || '',
    avatar_url: storedAvatar,
    phone: '138****8888', // 示例占位，实际可调接口获取
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

  // 预览新图片
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

      // 更新所有状态
      localStorage.setItem('avatar_url', newUrl)
      userInfo.value.avatar_url = newUrl
      oldAvatarUrl.value = newUrl // 更新备份
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
/* 页面容器与背景 */
.page-wrapper {
  min-height: 100vh;
  background-color: #f0f2f5;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  position: relative;
  overflow: hidden;
}

.bg-shape {
  position: absolute;
  top: -10%;
  right: -10%;
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(0, 137, 123, 0.1) 0%, rgba(255, 255, 255, 0) 70%);
  border-radius: 50%;
  pointer-events: none;
}

.content-container {
  width: 100%;
  max-width: 900px;
  z-index: 1;
  animation: slideUp 0.6s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 卡片整体 */
.profile-card {
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.08);
  border: none;
}

.profile-layout {
  min-height: 500px;
  display: flex;
}

/* 左侧面板 */
.left-panel {
  background: linear-gradient(135deg, #00695c 0%, #00897b 100%);
  color: white;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  position: relative;
  padding: 40px 20px;
  text-align: center;
}

.panel-content {
  position: relative;
  z-index: 2;
  width: 100%;
}

.circle-deco {
  position: absolute;
  bottom: -50px;
  left: -50px;
  width: 200px;
  height: 200px;
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 50%;
}

/* 头像区域 */
.avatar-container {
  margin-bottom: 25px;
  position: relative;
}

.avatar-wrapper {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  border: 4px solid rgba(255, 255, 255, 0.3);
  overflow: hidden;
  position: relative;
  cursor: pointer;
  transition: all 0.3s ease;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-wrapper:hover {
  border-color: white;
  transform: scale(1.05);
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  font-size: 48px;
  font-weight: bold;
  color: #00897b;
}

/* 悬停遮罩 */
.avatar-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
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

.upload-text {
  font-size: 12px;
  margin-top: 5px;
}

.upload-actions {
  margin-top: 15px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: center;
}

.cancel-btn {
  color: rgba(255, 255, 255, 0.8);
}
.cancel-btn:hover {
  color: white;
}

.display-name {
  font-size: 24px;
  margin: 0 0 10px 0;
  font-weight: 600;
}

.join-date {
  margin-top: 15px;
  font-size: 12px;
  opacity: 0.7;
}

/* 右侧面板 */
.right-panel {
  background: white;
  padding: 40px;
  display: flex;
  flex-direction: column;
}

.form-header {
  margin-bottom: 30px;
  border-bottom: 1px solid #f0f0f0;
  padding-bottom: 15px;
}

.form-header h3 {
  font-size: 22px;
  color: #333;
  margin: 0 0 8px 0;
}

.subtitle {
  color: #999;
  font-size: 14px;
  margin: 0;
}

.edit-form {
  flex: 1;
}

.form-tip {
  font-size: 12px;
  color: #999;
  margin-top: 6px;
  display: block;
}

.action-footer {
  margin-top: 40px;
  display: flex;
  justify-content: flex-end;
  gap: 15px;
}

.save-btn {
  padding: 12px 30px;
  font-weight: 600;
  background-color: #00897b;
  border-color: #00897b;
}

.save-btn:hover {
  background-color: #00695c;
  border-color: #00695c;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .profile-layout {
    flex-direction: column;
  }

  .left-panel {
    padding: 30px 20px;
  }

  .right-panel {
    padding: 30px 20px;
  }

  .action-footer {
    justify-content: space-between;
  }
}
</style>
