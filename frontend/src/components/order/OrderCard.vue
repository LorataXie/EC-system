<template>
  <div class="order-card" @click="$router.push(`/orders/${order.id}`)">
    <div class="order-header">
      <span>订单编号：{{ order.id?.substring(0,8) }}...</span>
      <el-tag :type="ORDER_STATUS_COLORS[order.status]" size="small">{{ ORDER_STATUS[order.status] || order.status }}</el-tag>
    </div>
    <div class="order-items">
      <div v-for="item in order.items" :key="item.id" class="order-item">
        <div class="item-info">
          <p>{{ item.product_name }}</p>
          <p class="item-spec">{{ formatPrice(item.price) }} x {{ item.quantity }}</p>
        </div>
        <span class="item-subtotal">{{ formatPrice(item.subtotal) }}</span>
      </div>
    </div>
    <div class="order-footer">
      <span>共 {{ order.items?.length || 0 }} 件</span>
      <span>总额：<strong class="total-amount">{{ formatPrice(order.total_amount) }}</strong></span>
    </div>
  </div>
</template>

<script setup>
import { formatPrice } from '@/utils/format'
import { ORDER_STATUS, ORDER_STATUS_COLORS } from '@/utils/constants'

defineProps({ order: { type: Object, required: true } })
</script>

<style scoped>
.order-card { background: #fff; border-radius: 8px; padding: 16px; margin-bottom: 16px; cursor: pointer; }
.order-header { display: flex; justify-content: space-between; padding-bottom: 12px; border-bottom: 1px solid #eee; }
.order-items { padding: 12px 0; }
.order-item { display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }
.item-info { flex: 1; font-size: 13px; }
.item-spec { color: #999; margin-top: 4px; }
.item-subtotal { font-weight: 600; }
.order-footer { display: flex; justify-content: space-between; padding-top: 12px; border-top: 1px solid #eee; }
.total-amount { color: #e4393c; font-size: 16px; }
</style>
