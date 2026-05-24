import request from './request'

export function login(data) {
  return request.post('/auth/login', data)
}

export function register(data) {
  return request.post('/auth/register', data)
}

export function logout(refresh) {
  return request.post('/auth/logout', { refresh })
}

export function refreshToken(refresh) {
  return request.post('/auth/token/refresh', { refresh })
}

export function getProfile() {
  return request.get('/profile/me')
}

export function updateUser(data) {
  return request.patch('/profile/me', data)
}
