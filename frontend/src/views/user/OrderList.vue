<template>
  <div class="page">
    <h2>我的订单</h2>
    <div class="status-filter">
      <el-radio-group v-model="statusFilter" @change="loadOrders" size="small">
        <el-radio-button value="">全部</el-radio-button>
        <el-radio-button v-for="(label,key) in STATUS_MAP" :key="key" :value="key">{{ label }}</el-radio-button>
      </el-radio-group>
    </div>
    <div v-if="orderStore.orders.length">
      <OrderCard v-for="order in orderStore.orders" :key="order.id" :order="order" />
    </div>
    <el-empty v-else description="暂无订单" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useOrderStore } from '@/stores/order'
import { ORDER_STATUS as STATUS_MAP } from '@/utils/constants'
import OrderCard from '@/components/order/OrderCard.vue'

const orderStore = useOrderStore()
const statusFilter = ref('')

async function loadOrders() {
  await orderStore.fetchOrders(statusFilter.value ? { status: statusFilter.value } : {})
}
onMounted(() => loadOrders())
</script>

<style scoped>
h2 { margin-bottom: 16px; }
.status-filter { margin-bottom: 16px; }
</style>
