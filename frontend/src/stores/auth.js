// ============================================================
// 认证状态管理 (Pinia Store)
// 管理：用户信息、Token、登录/注册/登出/获取用户信息
// ============================================================

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
// 后端认证 API 方法
import { login as apiLogin, register as apiRegister, logout as apiLogout, getProfile } from '@/api/auth'
// localStorage 读写工具
import { getToken, setToken, removeToken, getRefreshToken, setRefreshToken, removeRefreshToken } from '@/utils/storage'

export const useAuthStore = defineStore('auth', () => {
  // ----- 状态 -----
  // 当前登录用户对象（null = 未登录）
  const user = ref(null)
  // access token，初始化时尝试从 localStorage 恢复
  const token = ref(getToken() || '')

  // ----- 计算属性 -----
  // 是否已认证（token 非空即为已登录）
  const isAuthenticated = computed(() => !!token.value)
  // 是否是管理员（依赖用户的 is_staff 字段）
  const isAdmin = computed(() => user.value?.is_staff ?? false)

  // 登录：调用 API 获取 token，写入 Store 和 localStorage
  async function login(data) {
    const res = await apiLogin(data)
    token.value = res.data.access
    user.value = res.data.user
    setToken(res.data.access)
    setRefreshToken(res.data.refresh)
  }

  // 注册：同登录流程，注册后自动登录
  async function register(data) {
    const res = await apiRegister(data)
    token.value = res.data.access
    user.value = res.data.user
    setToken(res.data.access)
    setRefreshToken(res.data.refresh)
  }

  // 登出：调服务端登出接口（失败可忽略），然后清除本地状态
  async function logout() {
    try {
      await apiLogout(getRefreshToken())
    } catch (e) {
      // 即使服务端报错，也继续清除本地状态
    }
    token.value = ''
    user.value = null
    removeToken()
    removeRefreshToken()
  }

  // 获取当前用户信息（用于页面刷新后恢复登录态）
  async function fetchUser() {
    try {
      const res = await getProfile()
      // 接口直接返回用户对象，无嵌套的 profile 字段
      user.value = res.data
    } catch (e) {
      // 获取失败 = token 失效，清除状态
      token.value = ''
      user.value = null
      removeToken()
      removeRefreshToken()
    }
  }

  // 暴露给组件使用
  return { user, token, isAuthenticated, isAdmin, login, register, logout, fetchUser }
})
