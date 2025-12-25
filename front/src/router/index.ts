console.log('🔥 路由文件正在加载！')
import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import AdminDashboard from '../views/Admin/Dashboard.vue'
import Login from '../views/Auth/Login.vue'
import Register from '../views/Auth/Register.vue'
import Test from '../views/Test.vue'
import Questionnaire from '../views/Assessment/QuestionnaireView.vue'
import ReportView from '../views/Assessment/ReportView.vue'
// ConsultationSelect 也可以改为动态导入，或者保持顶部引入
import ConsultationSelect from '../views/Consultation/ConsultationSelect.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login',
    },
    {
      path: '/login',
      name: 'login',
      component: Login,
      meta: { guest: true },
    },
    {
      path: '/register',
      name: 'register',
      component: Register,
      meta: { guest: true },
    },
    {
      path: '/home',
      name: 'home',
      component: HomeView,
      meta: { requiresAuth: true, role: 'user' },
    },
    {
      path: '/admin/dashboard',
      name: 'adminDashboard',
      component: AdminDashboard,
      meta: { requiresAuth: true, role: 'admin' },
    },

    // --- 测评相关路由 ---
    {
      path: '/assessment',
      name: 'assessment',
      component: Questionnaire,
      meta: { requiresAuth: true, role: 'user' },
    },
    {
      path: '/report/:id',
      name: 'report',
      component: ReportView,
      meta: { requiresAuth: true, role: 'user' },
    },

    // --- AI 问诊相关路由 (核心修改) ---
    {
      path: '/consultation/select',
      name: 'consultationSelect',
      component: ConsultationSelect,
      meta: { requiresAuth: true, role: 'user' },
    },
    // 👇【新增】AI 聊天界面 (点击“开始问诊”后跳转的页面)
    // 注意：你需要确保 front/src/views/Consultation/ChatView.vue 文件存在（稍后我们会创建）
    // {
    //   path: '/consultation/chat',
    //   name: 'consultationChat',
    //   component: () => import('../views/Consultation/ChatView.vue'),
    //   meta: { requiresAuth: true, role: 'user' },
    // },

    // --- 历史记录模块路由 (导航栏入口) ---
    // 👇【新增】历史记录列表
    {
      path: '/history',
      name: 'historyList',
      component: () => import('../views/History/HistoryList.vue'),
      meta: { requiresAuth: true, role: 'user' },
    },
    // 👇【新增】历史问诊详情 (点击某次问诊记录)
    {
      path: '/history/consultation/:id',
      name: 'historyConsultationDetail',
      component: () => import('../views/History/ConsultationDetail.vue'),
      meta: { requiresAuth: true, role: 'user' },
    },
    // 👇【新增】个人资料页
    {
      path: '/profile',
      name: 'profile',
      component: () => import('../views/ProfileView.vue'),
      meta: { requiresAuth: true, role: 'user' },
    },
    { path: '/test', name: 'test', component: Test },
  ],
})

// 路由守卫保持不变
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const role = localStorage.getItem('role')

  if (to.meta.requiresAuth) {
    if (!token) {
      return next('/login')
    }
    if (to.meta.role && to.meta.role !== role) {
      return role === 'admin' ? next('/admin/dashboard') : next('/home')
    }
  } else if (to.meta.guest && token) {
    return role === 'admin' ? next('/admin/dashboard') : next('/home')
  }

  next()
})

console.log(
  '所有注册的路由:',
  router.getRoutes().map((r) => r.path),
)
export default router
