<template>
  <div>
    <h2>订单管理</h2>
    <div class="filter-bar">
      <el-select v-model="statusFilter" placeholder="订单状态" clearable @change="loadOrders" style="width:120px">
        <el-option v-for="(label,key) in STATUS_MAP" :key="key" :label="label" :value="key" />
      </el-select>
      <el-input v-model="userFilter" placeholder="用户ID" clearable @change="loadOrders" style="width:250px;margin-left:8px" />
      <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始" end-placeholder="结束" @change="loadOrders" style="margin-left:8px" />
    </div>
    <el-table :data="orders" v-loading="loading" stripe class="order-table">
      <el-table-column prop="id" label="订单ID" width="120">
        <template #default="{row}">{{ row.id?.substring(0,8) }}...</template>
      </el-table-column>
      <el-table-column label="金额" width="100">
        <template #default="{row}">{{ formatPrice(row.total_amount) }}</template>
      </el-table-column>
      <el-table-column label="状态" width="90">
        <template #default="{row}">
          <el-tag :type="STATUS_COLORS[row.status]" size="small">{{ STATUS_MAP[row.status]||row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="商品" min-width="160">
        <template #default="{row}">
          <span v-for="item in row.items" :key="item.id" style="margin-right:6px">{{ item.product_name }} x{{ item.quantity }}</span>
        </template>
      </el-table-column>
      <el-table-column label="物流" width="160">
        <template #default="{row}">
          <span v-if="row.tracking_number">{{ row.shipping_method }} {{ row.tracking_number }}</span>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column label="时间" width="100">
        <template #default="{row}">{{ formatDate(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="80">
        <template #default="{row}">
          <el-button v-if="row.status==='delivered'" size="small" type="success" @click="doComplete(row.id)">完成</el-button>
        </template>
      </el-table-column>
    </el-table>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { formatPrice, formatDate } from '@/utils/format'
import { ORDER_STATUS as STATUS_MAP, ORDER_STATUS_COLORS as STATUS_COLORS } from '@/utils/constants'
import request from '@/api/request'

const orders = ref([]); const loading = ref(false)
const userFilter = ref(''); const dateRange = ref([]); const statusFilter = ref('')
import { ElMessage } from 'element-plus'

onMounted(() => loadOrders())

async function doComplete(oid) {
  try {
    await request.post(`/admin/orders/${oid}/complete`)
    ElMessage.success('已标记为完成'); loadOrders()
  } catch(e) { ElMessage.error('操作失败') }
}

async function loadOrders() {
  loading.value = true
  try {
    const params = { page_size: 50 }
    if (userFilter.value) params.user_id = userFilter.value
    if (statusFilter.value) params.status = statusFilter.value
    if (dateRange.value?.length===2) {
      params.date_from = dateRange.value[0].toISOString(); params.date_to = dateRange.value[1].toISOString()
    }
    const res = await request.get('/admin/orders/all', { params })
    orders.value = res.data?.results || res.data || []
  } catch(e) { console.error('Failed to load orders') }
  finally { loading.value = false }
}
</script>

<style scoped>
h2 { margin-bottom: 16px; }
.filter-bar { margin-bottom: 16px; display: flex; align-items: center; }
.order-table { margin-top: 16px; }
</style>
