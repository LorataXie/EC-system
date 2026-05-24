import request from '../request'

export function getUsers(params) {
  return request.get('/admin/users/all', { params })
}

export function getUser(id) {
  return request.get(`/admin/users/${id}`)
}

export function updateUser(id, data) {
  return request.patch(`/admin/users/${id}`, data)
}

export function getUserLogs(id) {
  return request.get(`/admin/users/${id}/logs`)
}
