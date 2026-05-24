<template>
  <div v-loading="loading">
    <h2>用户详情</h2>
    <div v-if="userInfo" class="user-info">
      <p><strong>邮箱：</strong>{{ userInfo.email }}</p>
      <p><strong>用户名：</strong>{{ userInfo.username }}</p>
      <p><strong>手机号：</strong>{{ userInfo.phone || '未绑定' }}</p>
      <p><strong>角色：</strong>{{ userInfo.is_staff ? '管理员' : '普通用户' }}</p>
      <p><strong>状态：</strong>{{ userInfo.is_active ? '正常' : '已禁用' }}</p>
      <p><strong>注册时间：</strong>{{ formatDateTime(userInfo.date_joined) }}</p>
    </div>
    <div class="user-meta" style="margin-top:24px">
      <p><strong>VIP：</strong>{{ userInfo.is_vip ? '是' : '否' }}</p>
      <p><strong>性别：</strong>{{ userInfo.gender || '未设置' }}</p>
      <p><strong>年龄：</strong>{{ userInfo.age || '未设置' }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { formatDateTime } from '@/utils/format'
import request from '@/api/request'

const route = useRoute()
const userInfo = ref(null)
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await request.get(`/admin/users/${route.params.id}`)
    userInfo.value = res.data
  } catch (e) {
    console.error('Failed to load user detail')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
h2 { margin-bottom: 16px; }
.user-info p { margin-bottom: 8px; }
</style>
