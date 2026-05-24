import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { getToken } from '@/utils/storage'

const routes = [
  {
    path: '/',
    component: () => import('@/layouts/DefaultLayout.vue'),
    children: [
      { path: '', name: 'Home', component: () => import('@/views/public/Home.vue') },
      { path: 'products', name: 'ProductList', component: () => import('@/views/public/ProductList.vue') },
      { path: 'products/:id', name: 'ProductDetail', component: () => import('@/views/public/ProductDetail.vue') },
      { path: 'cart', name: 'Cart', component: () => import('@/views/public/Cart.vue') },
      { path: 'checkout', name: 'Checkout', component: () => import('@/views/user/Checkout.vue'), meta: { requiresAuth: true } },
    ],
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/public/Login.vue'),
    meta: { guest: true },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/public/Register.vue'),
    meta: { guest: true },
  },
  {
    path: '/reset-password',
    name: 'ResetPassword',
    component: () => import('@/views/public/ResetPassword.vue'),
    meta: { guest: true },
  },
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
  {
    path: '/admin',
    component: () => import('@/layouts/AdminLayout.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      { path: '', name: 'Dashboard', component: () => import('@/views/admin/Dashboard.vue') },
      { path: 'users', name: 'AdminUsers', component: () => import('@/views/admin/UserList.vue') },
      { path: 'users/:id', name: 'AdminUserDetail', component: () => import('@/views/admin/UserDetail.vue') },
      { path: 'products', name: 'AdminProducts', component: () => import('@/views/admin/ProductList.vue') },
      { path: 'products/create', name: 'AdminProductCreate', component: () => import('@/views/admin/ProductForm.vue') },
      { path: 'products/:id/edit', name: 'AdminProductEdit', component: () => import('@/views/admin/ProductForm.vue') },
      { path: 'categories', name: 'AdminCategories', component: () => import('@/views/admin/CategoryList.vue') },
      { path: 'orders', name: 'AdminOrders', component: () => import('@/views/admin/OrderList.vue') },
      { path: 'orders/:id', name: 'AdminOrderDetail', component: () => import('@/views/admin/OrderDetail.vue') },
      { path: 'coupons', name: 'AdminCoupons', component: () => import('@/views/admin/CouponList.vue') },
      { path: 'coupons/create', name: 'AdminCouponCreate', component: () => import('@/views/admin/CouponForm.vue') },
      { path: 'analytics', name: 'AdminAnalytics', component: () => import('@/views/admin/Analytics.vue') },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore()

  if (getToken() && !authStore.user) {
    await authStore.fetchUser()
  }

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return next({ name: 'Login', query: { redirect: to.fullPath } })
  }

  if (to.meta.guest && authStore.isAuthenticated) {
    return next({ name: 'Home' })
  }

  if (to.meta.requiresAdmin && !authStore.isAdmin) {
    return next({ name: 'Home' })
  }

  next()
})

export default router
