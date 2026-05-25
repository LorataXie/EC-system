<!-- ============================================================ -->
<!-- 登录页 - 邮箱/手机号 + 密码登录                                    -->
<!-- 支持登录后重定向回来源页面                                          -->
<!-- ============================================================ -->
<template>
  <div class="auth-page">
    <div class="auth-card">
      <h2>登录</h2>

      <el-form :model="form" :rules="rules" ref="formRef" label-position="top">
        <!-- 账号：支持邮箱或手机号 -->
        <el-form-item label="邮箱或手机号" prop="account">
          <el-input v-model="form.account" placeholder="请输入邮箱或手机号" @keyup.enter="handleLogin" />
        </el-form-item>

        <!-- 密码 -->
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password @keyup.enter="handleLogin" />
        </el-form-item>

        <!-- 登录按钮 -->
        <el-form-item>
          <el-button type="primary" :loading="loading" block @click="handleLogin">登录</el-button>
        </el-form-item>
      </el-form>

      <!-- 底部链接：注册 / 忘记密码 -->
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

// 表单数据（reactive 实现双向绑定）
const form = reactive({ account: '', password: '' })

// 表单验证规则
const rules = {
  account: [{ required: true, message: '请输入邮箱或手机号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码' }, { min: 8, message: '密码至少8位' }],
}

// 登录处理：验证表单 → 调 store.login → 成功后跳转
async function handleLogin() {
  // 表单验证，失败则中止
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await authStore.login({ account: form.account, password: form.password })
    ElMessage.success('登录成功')
    // 登录后重定向到来源页面，无来源则去首页
    router.push(route.query.redirect || '/')
  } catch (e) {
    ElMessage.error(e.response?.data?.data?.detail || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* 居中卡片布局 */
.auth-page { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: #f0f2f5; }
.auth-card { width: 400px; padding: 40px; background: #fff; border-radius: 8px; box-shadow: 0 2px 12px rgba(0,0,0,0.1); }
.auth-card h2 { text-align: center; margin-bottom: 24px; }
.switch-link { text-align: center; color: #999; margin-top: 8px; }
.switch-link a { color: #409eff; }
</style>
