import axios from 'axios'
import { getToken, setToken, getRefreshToken, removeToken, removeRefreshToken } from '@/utils/storage'

const request = axios.create({
  baseURL: '/api/v1',
  timeout: 15000,
})

request.interceptors.request.use(
  (config) => {
    const token = getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

let isRefreshing = false
let failedQueue = []

function processQueue(error, token = null) {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error)
    } else {
      resolve(token)
    }
  })
  failedQueue = []
}

request.interceptors.response.use(
  (response) => response.data,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        }).then(() => {
          originalRequest.headers.Authorization = `Bearer ${getToken()}`
          return request(originalRequest)
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      const refreshToken = getRefreshToken()
      if (!refreshToken) {
        removeToken()
        removeRefreshToken()
        window.location.href = '/login'
        return Promise.reject(error)
      }

      try {
        const response = await axios.post('/api/v1/auth/token/refresh', {
          refresh: refreshToken,
        })
        const { access, refresh } = response.data.data
        setToken(access)
        setRefreshToken(refresh)
        processQueue(null, access)
        originalRequest.headers.Authorization = `Bearer ${access}`
        return request(originalRequest)
      } catch (refreshError) {
        processQueue(refreshError, null)
        removeToken()
        removeRefreshToken()
        window.location.href = '/login'
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(error)
  }
)

export default request
