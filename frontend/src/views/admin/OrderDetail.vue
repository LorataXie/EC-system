<template>
  <div v-loading="loading">
    <h2>订单详情 - {{ order?.id }}</h2>
    <div v-if="order">
      <OrderItemTable :items="order.items || []" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import OrderItemTable from '@/components/order/OrderItemTable.vue'
import request from '@/api/request'

const route = useRoute()
const order = ref(null)
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await request.get(`/admin/orders/${route.params.id}/detail`)
    order.value = res.data
  } catch (e) {
    console.error('Failed to load order')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
h2 { margin-bottom: 16px; }
</style>
