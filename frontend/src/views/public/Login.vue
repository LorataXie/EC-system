<template>
  <div class="auth-page">
    <div class="auth-card">
      <h2>登录</h2>
      <el-form :model="form" :rules="rules" ref="formRef" label-position="top">
        <el-form-item label="邮箱或手机号" prop="account">
          <el-input v-model="form.account" placeholder="请输入邮箱或手机号" @keyup.enter="handleLogin" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password @keyup.enter="handleLogin" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" block @click="handleLogin">登录</el-button>
        </el-form-item>
      </el-form>
      <p class="switch-link">
        还没有账号？<router-link to="/register">立即注册</router-link>
        <span style="margin:0 8px">|</span>
        <router-link to="/reset-password">忘记密码</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({ account: '', password: '' })

const rules = {
  account: [{ required: true, message: '请输入邮箱或手机号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码' }, { min: 8, message: '密码至少8位' }],
}

async function handleLogin() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    await authStore.login({ account: form.account, password: form.password })
    ElMessage.success('登录成功')
    router.push(route.query.redirect || '/')
  } catch (e) {
    ElMessage.error(e.response?.data?.data?.detail || '登录失败')
  } finally { loading.value = false }
}
</script>

<style scoped>
.auth-page { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: #f0f2f5; }
.auth-card { width: 400px; padding: 40px; background: #fff; border-radius: 8px; box-shadow: 0 2px 12px rgba(0,0,0,0.1); }
.auth-card h2 { text-align: center; margin-bottom: 24px; }
.switch-link { text-align: center; color: #999; margin-top: 8px; }
.switch-link a { color: #409eff; }
</style>
