// ============================================================
// 路由配置 - 全部路由定义与导航守卫
// ============================================================

// Vue Router 核心：createRouter 创建路由、createWebHistory HTML5 History 模式
import { createRouter, createWebHistory } from 'vue-router'
// 认证状态 Store，用于导航守卫中判断登录状态和角色
import { useAuthStore } from '@/stores/auth'
// 工具函数：从 localStorage 读取 token
import { getToken } from '@/utils/storage'

// ----- 路由表 -----
const routes = [
  // ========== 公开商城路由（默认布局 - 包含页头/页脚） ==========
  {
    path: '/',
    component: () => import('@/layouts/DefaultLayout.vue'),
    children: [
      // 首页
      { path: '', name: 'Home', component: () => import('@/views/public/Home.vue') },
      // 商品列表页 - 支持分类/关键词/价格筛选
      { path: 'products', name: 'ProductList', component: () => import('@/views/public/ProductList.vue') },
      // 商品详情页 - 动态路由参数 :id
      { path: 'products/:id', name: 'ProductDetail', component: () => import('@/views/public/ProductDetail.vue') },
      // 购物车页
      { path: 'cart', name: 'Cart', component: () => import('@/views/public/Cart.vue') },
      // 结算页 - 需要登录
      { path: 'checkout', name: 'Checkout', component: () => import('@/views/user/Checkout.vue'), meta: { requiresAuth: true } },
    ],
  },

  // ========== 认证相关路由（独立页面，无布局） ==========
  { path: '/login', name: 'Login', component: () => import('@/views/public/Login.vue'), meta: { guest: true } },
  { path: '/register', name: 'Register', component: () => import('@/views/public/Register.vue'), meta: { guest: true } },
  { path: '/reset-password', name: 'ResetPassword', component: () => import('@/views/public/ResetPassword.vue'), meta: { guest: true } },

  // ========== 用户中心路由（用户布局 - 含侧边栏） ==========
  {
    path: '/profile',
    component: () => import('@/layouts/UserLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', name: 'Profile', component: () => import('@/views/user/Profile.vue') },
      { path: 'addresses', name: 'AddressList', component: () => import('@/views/user/AddressList.vue') },
      { path: 'statistics', name: 'Statistics', component: () => import('@/views/user/Statistics.vue') },
    ],
  },
  {
    path: '/orders',
    component: () => import('@/layouts/UserLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', name: 'OrderList', component: () => import('@/views/user/OrderList.vue') },
      { path: ':id', name: 'OrderDetail', component: () => import('@/views/user/OrderDetail.vue') },
    ],
  },

  // ========== 后台管理路由（管理布局 + 角色鉴权） ==========
  {
    path: '/admin',
    component: () => import('@/layouts/AdminLayout.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      // 仪表盘首页
      { path: '', name: 'Dashboard', component: () => import('@/views/admin/Dashboard.vue') },
      // 用户 CRUD
      { path: 'users', name: 'AdminUsers', component: () => import('@/views/admin/UserList.vue') },
      { path: 'users/:id', name: 'AdminUserDetail', component: () => import('@/views/admin/UserDetail.vue') },
      // 商品 CRUD
      { path: 'products', name: 'AdminProducts', component: () => import('@/views/admin/ProductList.vue') },
      { path: 'products/create', name: 'AdminProductCreate', component: () => import('@/views/admin/ProductForm.vue') },
      { path: 'products/:id/edit', name: 'AdminProductEdit', component: () => import('@/views/admin/ProductForm.vue') },
      // 分类管理
      { path: 'categories', name: 'AdminCategories', component: () => import('@/views/admin/CategoryList.vue') },
      // 订单管理
      { path: 'orders', name: 'AdminOrders', component: () => import('@/views/admin/OrderList.vue') },
      { path: 'orders/:id', name: 'AdminOrderDetail', component: () => import('@/views/admin/OrderDetail.vue') },
      // 优惠券管理
      { path: 'coupons', name: 'AdminCoupons', component: () => import('@/views/admin/CouponList.vue') },
      { path: 'coupons/create', name: 'AdminCouponCreate', component: () => import('@/views/admin/CouponForm.vue') },
      // 数据分析
      { path: 'analytics', name: 'AdminAnalytics', component: () => import('@/views/admin/Analytics.vue') },
    ],
  },
]

// 创建路由实例 - 使用 HTML5 History 模式（无 # 号）
const router = createRouter({
  history: createWebHistory(),
  routes,
})

// ===== 全局前置导航守卫 =====
// 作用：自动恢复用户状态、拦截未登录访问、重定向已登录访客
router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore()

  // 如果本地有 token 但 Store 中无用户信息，自动拉取用户信息
  // 场景：用户刷新页面后，token 还在 localStorage，需要恢复登录态
  if (getToken() && !authStore.user) {
    await authStore.fetchUser()
  }

  // 需要登录但未登录 → 跳转登录页，并带上 redirect 参数以便登录后返回
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return next({ name: 'Login', query: { redirect: to.fullPath } })
  }

  // 访客页面（如登录/注册）但已登录 → 跳转首页
  if (to.meta.guest && authStore.isAuthenticated) {
    return next({ name: 'Home' })
  }

  // 需要管理员权限但不是管理员 → 跳转首页
  if (to.meta.requiresAdmin && !authStore.isAdmin) {
    return next({ name: 'Home' })
  }

  next()
})

export default router
