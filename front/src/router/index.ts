import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import AdminDashboard from '../views/Admin/Dashboard.vue'
import Login from '../views/Auth/Login.vue'
import Register from '../views/Auth/Register.vue'
import Test from '../views/Test.vue' //原有的App.vue
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login', // 默认跳转到登录页
    },
    {
      path: '/login',
      name: 'login',
      component: Login,
      meta: { guest: true }, // 不需要登录即可访问
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
      meta: { requiresAuth: true, role: 'user' }, // 需要普通用户权限
    },
    {
      path: '/admin/dashboard',
      name: 'adminDashboard',
      component: AdminDashboard,
      meta: { requiresAuth: true, role: 'admin' }, // 需要管理员权限
    },

    { path: '/test', name: 'test', component: Test },
  ],
})

// 修改后的路由守卫（仅限制未登录用户访问home）
// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const role = localStorage.getItem('role')

  // 需要登录的页面
  if (to.meta.requiresAuth) {
    if (!token) {
      return next('/login')
    }

    // 检查角色权限
    if (to.meta.role && to.meta.role !== role) {
      // 角色不匹配时跳转
      return role === 'admin' ? next('/admin/dashboard') : next('/home')
    }
  }
  // 已登录用户不能访问登录/注册页
  else if (to.meta.guest && token) {
    return role === 'admin' ? next('/admin/dashboard') : next('/home')
  }

  next()
})

export default router
