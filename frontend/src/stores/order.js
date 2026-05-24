import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getOrders, createOrder, getOrder } from '@/api/orders'

export const useOrderStore = defineStore('order', () => {
  const orders = ref([])
  const currentOrder = ref(null)
  const total = ref(0)

  async function fetchOrders(params = {}) {
    try {
      const res = await getOrders(params)
      orders.value = res.data?.results || []
      total.value = res.data?.count || 0
    } catch (e) {
      console.error('Failed to fetch orders')
    }
  }

  async function fetchOrder(id) {
    try {
      const res = await getOrder(id)
      currentOrder.value = res.data
      return res.data
    } catch (e) {
      console.error('Failed to fetch order')
      return null
    }
  }

  async function place(data) {
    const res = await createOrder(data)
    return res.data
  }

  return { orders, currentOrder, total, fetchOrders, fetchOrder, place }
})
