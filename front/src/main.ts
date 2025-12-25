// front/src/main.ts
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

import './assets/main.css' // 确保引入了刚才修改的样式

// === 新增代码开始 ===
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
// === 新增代码结束 ===

const app = createApp(App)

app.use(createPinia())
app.use(router)
// === 新增代码 ===
app.use(ElementPlus)
// ===============
// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}
app.mount('#app')
