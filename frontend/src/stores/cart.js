// ============================================================
// 购物车状态管理 (Pinia Store)
// 管理：购物车数据、增/改/删商品、购物车总数量
// ============================================================

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
// 购物车 API 方法
import { getCart, addItem, updateItem, removeItem } from '@/api/cart'

export const useCartStore = defineStore('cart', () => {
  // 购物车数据对象：items 数组、total_amount 总金额、item_count 总数量
  const cart = ref({ items: [], total_amount: 0, item_count: 0 })

  // 计算购物车中商品种类数（用于徽标显示）
  const cartCount = computed(() => cart.value.items?.length || 0)

  // 从服务器获取最新购物车数据
  async function fetchCart() {
    try {
      const res = await getCart()
      cart.value = res.data
    } catch (e) {
      console.error('Failed to fetch cart')
    }
  }

  // 添加商品到购物车，成功后自动刷新本地数据
  async function add(productId, quantity = 1) {
    const res = await addItem(productId, quantity)
    await fetchCart()
    return res
  }

  // 更新购物车中某商品的购买数量
  async function update(itemId, quantity) {
    await updateItem(itemId, quantity)
    await fetchCart()
  }

  // 从购物车中移除某商品
  async function remove(itemId) {
    await removeItem(itemId)
    await fetchCart()
  }

  return { cart, cartCount, fetchCart, add, update, remove }
})
