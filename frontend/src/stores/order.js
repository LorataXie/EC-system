// ============================================================
// 订单状态管理 (Pinia Store)
// 管理：订单列表（分页）、当前订单详情、下单操作
// ============================================================

import { defineStore } from 'pinia'
import { ref } from 'vue'
// 订单 API 方法
import { getOrders, createOrder, getOrder } from '@/api/orders'

export const useOrderStore = defineStore('order', () => {
  // 订单列表（当前页）
  const orders = ref([])
  // 当前查看的订单详情
  const currentOrder = ref(null)
  // 订单总条数（用于分页）
  const total = ref(0)

  // 分页获取订单列表
  async function fetchOrders(params = {}) {
    try {
      const res = await getOrders(params)
      orders.value = res.data?.results || []
      total.value = res.data?.count || 0
    } catch (e) {
      console.error('Failed to fetch orders')
    }
  }

  // 获取单个订单详情
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

  // 创建新订单（下单）
  async function place(data) {
    const res = await createOrder(data)
    return res.data
  }

  return { orders, currentOrder, total, fetchOrders, fetchOrder, place }
})
