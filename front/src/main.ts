// front/src/main.ts
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

import './assets/main.css' // 确保引入了刚才修改的样式

// === 新增代码开始 ===
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
// === 新增代码结束 ===

const app = createApp(App)

app.use(createPinia())
app.use(router)
// === 新增代码 ===
app.use(ElementPlus)
// ===============

app.mount('#app')
