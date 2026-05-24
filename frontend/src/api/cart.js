import request from './request'

export function getCart() {
  return request.get('/cart/my')
}

export function addItem(productId, quantity = 1) {
  return request.post('/cart/items', { product_id: productId, quantity })
}

export function updateItem(itemId, quantity) {
  return request.patch(`/cart/items/${itemId}`, { quantity })
}

export function removeItem(itemId) {
  return request.delete(`/cart/items/${itemId}`)
}

export function mergeCart() {
  return request.post('/cart/merge')
}
