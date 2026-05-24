import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as apiLogin, register as apiRegister, logout as apiLogout, getProfile } from '@/api/auth'
import { getToken, setToken, removeToken, getRefreshToken, setRefreshToken, removeRefreshToken } from '@/utils/storage'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(getToken() || '')

  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.is_staff ?? false)

  async function login(data) {
    const res = await apiLogin(data)
    token.value = res.data.access
    user.value = res.data.user
    setToken(res.data.access)
    setRefreshToken(res.data.refresh)
  }

  async function register(data) {
    const res = await apiRegister(data)
    token.value = res.data.access
    user.value = res.data.user
    setToken(res.data.access)
    setRefreshToken(res.data.refresh)
  }

  async function logout() {
    try {
      await apiLogout(getRefreshToken())
    } catch (e) {
      // ignore
    }
    token.value = ''
    user.value = null
    removeToken()
    removeRefreshToken()
  }

  async function fetchUser() {
    try {
      const res = await getProfile()
      // User is returned directly, no nested profile object
      user.value = res.data
    } catch (e) {
      token.value = ''
      user.value = null
      removeToken()
      removeRefreshToken()
    }
  }

  return { user, token, isAuthenticated, isAdmin, login, register, logout, fetchUser }
})
