import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getCart, addItem, updateItem, removeItem } from '@/api/cart'

export const useCartStore = defineStore('cart', () => {
  const cart = ref({ items: [], total_amount: 0, item_count: 0 })

  const cartCount = computed(() => cart.value.items?.length || 0)

  async function fetchCart() {
    try {
      const res = await getCart()
      cart.value = res.data
    } catch (e) {
      console.error('Failed to fetch cart')
    }
  }

  async function add(productId, quantity = 1) {
    const res = await addItem(productId, quantity)
    await fetchCart()
    return res
  }

  async function update(itemId, quantity) {
    await updateItem(itemId, quantity)
    await fetchCart()
  }

  async function remove(itemId) {
    await removeItem(itemId)
    await fetchCart()
  }

  return { cart, cartCount, fetchCart, add, update, remove }
})
