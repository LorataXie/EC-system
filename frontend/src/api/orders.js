import request from './request'

export function getOrders(params = {}) {
  return request.get('/orders/my', { params })
}

export function createOrder(data) {
  return request.post('/orders/place', data)
}

export function getOrder(id) {
  return request.get(`/orders/${id}/detail`)
}
