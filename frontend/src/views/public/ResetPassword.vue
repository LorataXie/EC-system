<template>
  <div class="auth-page">
    <div class="auth-card">
      <h2>找回密码</h2>
      <el-form :model="form" :rules="rules" ref="formRef" label-position="top">
        <el-form-item label="邮箱" prop="target">
          <div class="input-row">
            <el-input v-model="form.target" placeholder="输入注册时的邮箱" />
            <el-button type="primary" :disabled="countdown>0" :loading="sendLoading" @click="sendCode" class="input-btn">
              {{ countdown>0 ? `${countdown}s` : '发送验证码' }}
            </el-button>
          </div>
        </el-form-item>
        <el-form-item label="验证码" prop="code">
          <el-input v-model="form.code" placeholder="6位验证码" maxlength="6" />
        </el-form-item>
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="form.new_password" type="password" placeholder="至少8位" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" block @click="handleReset">重置密码</el-button>
        </el-form-item>
      </el-form>
      <p class="switch-link"><router-link to="/login">返回登录</router-link></p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import request from '@/api/request'
import { ElMessage } from 'element-plus'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false), sendLoading = ref(false), countdown = ref(0)

const form = reactive({ target: '', code: '', new_password: '' })

const rules = {
  target: [{ required: true, message: '请输入邮箱' }, { type: 'email', message: '邮箱格式不正确' }],
  code: [{ required: true, message: '请输入验证码' }],
  new_password: [{ required: true, message: '请输入新密码' }, { min: 8, message: '至少8位' }],
}

async function sendCode() {
  try { await formRef.value.validateField('target') } catch { return }
  sendLoading.value = true
  try {
    await request.post('/auth/password/reset', { target: form.target })
    ElMessage.success('验证码已发送')
    countdown.value = 60
    const t = setInterval(() => { countdown.value--; if (countdown.value <= 0) clearInterval(t) }, 1000)
  } catch (e) {
    ElMessage.error(e.response?.data?.data?.target?.[0] || e.response?.data?.data?.detail || '发送失败')
  } finally { sendLoading.value = false }
}

async function handleReset() {
  const v = await formRef.value.validate().catch(() => false)
  if (!v) return
  loading.value = true
  try {
    await request.post('/auth/password/reset/confirm', form)
    ElMessage.success('密码已重置，请重新登录')
    router.push('/login')
  } catch (e) {
    const d = e.response?.data?.data
    ElMessage.error(typeof d === 'object' ? Object.values(d).flat().join(', ') : '重置失败')
  } finally { loading.value = false }
}
</script>

<style scoped>
.auth-page { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: #f0f2f5; }
.auth-card { width: 420px; padding: 40px; background: #fff; border-radius: 8px; box-shadow: 0 2px 12px rgba(0,0,0,0.1); }
.auth-card h2 { text-align: center; margin-bottom: 24px; }
.input-row { display: flex; gap: 8px; }
.input-row .el-input { flex: 1; }
.input-btn { flex-shrink: 0; min-width: 110px; }
.switch-link { text-align: center; color: #999; margin-top: 8px; }
.switch-link a { color: #409eff; }
</style>
