import request from './request'

export function getCategories(params = {}) {
  return request.get('/categories', { params })
}

export function getCategory(id) {
  return request.get(`/categories/${id}`)
}

export function getProducts(params = {}) {
  return request.get('/products', { params })
}

export function getProduct(id) {
  return request.get(`/products/${id}`)
}

export function getProductReviews(id, params = {}) {
  return request.get(`/products/${id}/reviews`, { params })
}
