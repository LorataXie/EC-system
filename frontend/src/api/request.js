// ============================================================
// Axios 实例封装 - 统一的 HTTP 请求客户端
// 功能：基础配置、Bearer Token 自动注入、401 自动刷新 Token、并发请求队列管理
// ============================================================

import axios from 'axios'
// localStorage 工具：读写 token 和 refreshToken
import { getToken, setToken, getRefreshToken, removeToken, removeRefreshToken } from '@/utils/storage'

// ----- 创建 Axios 实例 -----
const request = axios.create({
  // 所有请求都自动拼接 /api/v1 前缀
  baseURL: '/api/v1',
  // 超时时间 15 秒
  timeout: 15000,
})

// ===== 请求拦截器：自动附带 Authorization Header =====
request.interceptors.request.use(
  (config) => {
    // 从 localStorage 读取 access token
    const token = getToken()
    if (token) {
      // 以 Bearer 格式附加到请求头
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// ===== 响应拦截器：Token 刷新队列机制 =====

// 标记是否正在刷新 token（防止并发刷新）
let isRefreshing = false

// 存储刷新期间暂挂的请求队列
// 每个元素包含 resolve / reject，token 刷新完成后统一处理
let failedQueue = []

/**
 * 处理刷新队列
 * @param {Error|null} error - 刷新失败时为错误对象，成功时为 null
 * @param {string|null} token - 刷新成功时为新的 access token
 */
function processQueue(error, token = null) {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) {
      // 刷新失败 → 拒绝队列中的所有请求
      reject(error)
    } else {
      // 刷新成功 → 用新 token resolve
      resolve(token)
    }
  })
  // 清空队列
  failedQueue = []
}

request.interceptors.response.use(
  // 成功响应：直接返回 response.data，业务代码无需再解包
  (response) => response.data,
  // 错误响应：处理 401 刷新逻辑
  async (error) => {
    const originalRequest = error.config

    // 当收到 401 且该请求尚未重试过
    if (error.response?.status === 401 && !originalRequest._retry) {
      // 如果已经在刷新中，将当前请求加入等待队列
      // 避免多个请求同时触发多次 token 刷新
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        }).then(() => {
          // 刷新成功后，用新 token 重试原请求
          originalRequest.headers.Authorization = `Bearer ${getToken()}`
          return request(originalRequest)
        })
      }

      // 标记该请求已尝试重试
      originalRequest._retry = true
      // 开启刷新锁
      isRefreshing = true

      // 获取 refresh token
      const refreshToken = getRefreshToken()
      // 如果没有 refresh token，直接踢到登录页
      if (!refreshToken) {
        removeToken()
        removeRefreshToken()
        window.location.href = '/login'
        return Promise.reject(error)
      }

      try {
        // 调用刷新接口获取新的 token 对
        const response = await axios.post('/api/v1/auth/token/refresh', {
          refresh: refreshToken,
        })
        const { access, refresh } = response.data.data

        // 更新 localStorage 中的 token
        setToken(access)
        setRefreshToken(refresh)

        // 处理等待队列中的请求（成功）
        processQueue(null, access)

        // 用新 token 重试原请求
        originalRequest.headers.Authorization = `Bearer ${access}`
        return request(originalRequest)
      } catch (refreshError) {
        // 刷新也失败 → 彻底清除登录状态
        processQueue(refreshError, null)
        removeToken()
        removeRefreshToken()
        window.location.href = '/login'
        return Promise.reject(refreshError)
      } finally {
        // 无论刷新成功或失败，都释放锁
        isRefreshing = false
      }
    }

    // 非 401 错误直接透传，由调用方处理
    return Promise.reject(error)
  }
)

export default request
