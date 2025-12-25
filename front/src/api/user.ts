import api from './auth' // 复用 auth.ts 里的 axios 实例

// 修改昵称
export const updateProfile = async (uid: string | number, nickname: string) => {
  const response = await api.post('/user/profile', { uid, nickname })
  return response.data
}

// 上传头像
export const uploadAvatar = async (uid: string | number, file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('uid', String(uid))

  const response = await api.post('/user/avatar', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}
