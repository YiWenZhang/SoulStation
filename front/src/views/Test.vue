//原来的App.vue
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'

const message = ref('正在连接...')
const status = ref('loading')

onMounted(async () => {
  try {
    const res = await axios.get('/api/test')

    // 🔍 暴力调试：直接把整个包裹转成字符串显示出来
    // 这样我们就能看见到底收到了什么，是 .msg 还是 .message 还是别的
    message.value = JSON.stringify(res.data)

    status.value = 'success'
  } catch (err) {
    // 1. 不要在 catch 后面的括号里写类型
    console.error('连接失败:', err)

    // 2. 判断一下 err 是不是一个标准的 Error 对象
    if (err instanceof Error) {
      message.value = '连接失败: ' + err.message
    } else {
      message.value = '连接失败: 未知错误'
    }

    status.value = 'error'
  }
})
</script>

<template>
  <div class="box">
    <h1>全栈联调测试</h1>
    <div :class="status">
      <h2>{{ message }}</h2>
    </div>
  </div>
</template>

<style scoped>
.box {
  text-align: center;
  margin-top: 60px;
}
.success {
  color: green;
  border: 2px solid green;
  padding: 20px;
}
.error {
  color: red;
  border: 2px solid red;
  padding: 20px;
}
.loading {
  color: gray;
}
</style>
