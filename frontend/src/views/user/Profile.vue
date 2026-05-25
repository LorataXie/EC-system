<template>
  <div class="page">
    <h2>个人信息</h2>
    <el-form :model="form" label-width="80px" class="profile-form">
      <el-form-item label="邮箱">
        <el-input :model-value="authStore.user?.email" disabled />
      </el-form-item>
      <el-form-item label="用户名">
        <el-input v-model="form.username" />
      </el-form-item>
      <el-form-item label="手机号">
        <el-input v-model="form.phone" />
      </el-form-item>
      <el-form-item label="昵称">
        <el-input v-model="form.nickname" />
      </el-form-item>
      <el-form-item label="性别">
        <el-radio-group v-model="form.gender">
          <el-radio value="male">男</el-radio>
          <el-radio value="female">女</el-radio>
          <el-radio value="other">其他</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="年龄">
        <el-input-number v-model="form.age" :min="1" :max="150" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" :loading="saving" @click="handleSave">保存修改</el-button>
      </el-form-item>
      <el-divider />
      <el-form-item>
        <el-popconfirm title="注销后所有数据将被删除且无法恢复，确定注销？" @confirm="handleDeleteAccount">
          <template #reference>
            <el-button type="danger" plain>注销账户</el-button>
          </template>
        </el-popconfirm>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { reactive, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { getProfile, updateUser } from '@/api/auth'
import { ElMessage } from 'element-plus'
import request from '@/api/request'

const router = useRouter()
const authStore = useAuthStore()
const saving = ref(false)

const form = reactive({
  username: '',
  phone: '',
  nickname: '',
  gender: '',
  age: null,
})

onMounted(async () => {
  try {
    const res = await getProfile()
    const user = res.data
    form.username = user?.username || ''
    form.phone = user?.phone || ''
    form.nickname = user?.nickname || ''
    form.gender = user?.gender || ''
    form.age = user?.age || null
  } catch (e) {
    console.error('Failed to load profile')
  }
})

async function handleSave() {
  saving.value = true
  try {
    await updateUser(form)
    // Refresh the auth store with updated user data
    await authStore.fetchUser()
    ElMessage.success('个人信息已更新')
  } catch (e) {
    ElMessage.error('更新失败')
  } finally {
    saving.value = false
  }
}

async function handleDeleteAccount() {
  try {
    await request.post('/profile/delete-account')
    authStore.logout()
    ElMessage.success('账户已注销')
    router.push('/')
  } catch(e) { ElMessage.error('注销失败') }
}
</script>

<style scoped>
h2 { margin-bottom: 20px; }
.profile-form { max-width: 480px; }
</style>
