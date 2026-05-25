<template>
  <div v-loading="loading">
    <h2>用户详情</h2>
    <div v-if="userInfo" class="user-info">
      <p><strong>邮箱：</strong>{{ userInfo.email }}</p>
      <p><strong>用户名：</strong>{{ userInfo.username }}</p>
      <p><strong>手机号：</strong>{{ userInfo.phone||'未绑定' }}</p>
      <p><strong>角色：</strong>{{ userInfo.is_staff?'管理员':'普通用户' }}</p>
      <p><strong>VIP：</strong>{{ userInfo.is_vip?'是':'否' }}</p>
      <p><strong>状态：</strong>{{ userInfo.is_active?'正常':'已禁用' }}</p>
      <p><strong>消费总额：</strong>{{ formatPrice(userInfo.total_spent||0) }}</p>
      <p><strong>注册时间：</strong>{{ formatDateTime(userInfo.date_joined) }}</p>
    </div>
    <div v-if="logs.length" style="margin-top:24px">
      <h3>操作日志</h3>
      <el-table :data="logs" stripe size="small">
        <el-table-column prop="action" label="操作" width="120" />
        <el-table-column prop="detail" label="详情" />
        <el-table-column label="时间" width="170">
          <template #default="{row}">{{ formatDateTime(row.created_at) }}</template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { formatPrice, formatDateTime } from '@/utils/format'
import request from '@/api/request'

const route = useRoute()
const userInfo = ref(null)
const logs = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const [uRes, lRes] = await Promise.all([
      request.get(`/admin/users/${route.params.id}`),
      request.get(`/admin/users/${route.params.id}/logs`),
    ])
    userInfo.value = uRes.data
    logs.value = lRes.data || []
  } catch(e) { console.error('Failed to load') }
  finally { loading.value = false }
})
</script>

<style scoped>
h2 { margin-bottom:16px; }
.user-info p { margin-bottom:8px; }
</style>
