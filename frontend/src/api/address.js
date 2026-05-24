import request from './request'

export function getAddresses() {
  return request.get('/addresses')
}

export function createAddress(data) {
  return request.post('/addresses', data)
}

export function updateAddress(id, data) {
  return request.patch(`/addresses/${id}`, data)
}

export function deleteAddress(id) {
  return request.delete(`/addresses/${id}`)
}

export function setDefaultAddress(id) {
  return request.post(`/addresses/${id}/set-default`)
}
