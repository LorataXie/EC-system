<template>
  <div>
    <h2>用户管理</h2>
    <el-table :data="users" v-loading="loading" stripe>
      <el-table-column prop="email" label="邮箱" />
      <el-table-column prop="username" label="用户名" />
      <el-table-column prop="phone" label="手机号" />
      <el-table-column label="角色" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_staff ? 'danger' : 'info'" size="small">
            {{ row.is_staff ? '管理员' : '用户' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="消费总额" width="100">
        <template #default="{row}">{{ formatPrice(row.total_spent||0) }}</template>
      </el-table-column>
      <el-table-column label="VIP" width="80">
        <template #default="{ row }">
          <el-switch :model-value="row.is_vip" @change="toggleVip(row)" size="small" />
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
            {{ row.is_active ? '正常' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="date_joined" label="注册时间" width="180">
        <template #default="{ row }">{{ formatDateTime(row.date_joined) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button size="small" @click="$router.push(`/admin/users/${row.id}`)">查看</el-button>
          <el-button size="small" :type="row.is_active ? 'danger' : 'success'" @click="toggleUser(row)">
            {{ row.is_active ? '禁用' : '启用' }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { formatPrice, formatDateTime } from '@/utils/format'
import request from '@/api/request'
import { ElMessage } from 'element-plus'

const users = ref([])
const loading = ref(false)

onMounted(() => loadUsers())

async function loadUsers() {
  loading.value = true
  try {
    const res = await request.get('/admin/users', { params: { page_size: 100 } })
    users.value = res.data?.results || res.data || []
  } catch (e) {
    console.error('Failed to load users')
  } finally {
    loading.value = false
  }
}

async function toggleUser(user) {
  try {
    await request.patch(`/admin/users/${user.id}`, { is_active: !user.is_active })
    ElMessage.success(user.is_active ? '已禁用' : '已启用')
    loadUsers()
  } catch (e) { ElMessage.error('操作失败') }
}

async function toggleVip(user) {
  try {
    await request.patch(`/admin/users/${user.id}`, { is_vip: !user.is_vip })
    ElMessage.success(user.is_vip ? '已取消VIP' : '已设为VIP')
    loadUsers()
  } catch (e) { ElMessage.error('操作失败') }
}
</script>

<style scoped>
h2 { margin-bottom: 16px; }
</style>
