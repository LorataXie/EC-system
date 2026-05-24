import request from '../request'

export function getOverview() {
  return request.get('/admin/analytics/overview')
}

export function getSalesTrend(months = 6) {
  return request.get('/admin/analytics/sales-trend', { params: { months } })
}

export function getHotProducts(limit = 10) {
  return request.get('/admin/analytics/hot-products', { params: { limit } })
}

export function getRecentOrders(limit = 10) {
  return request.get('/admin/analytics/recent-orders', { params: { limit } })
}
