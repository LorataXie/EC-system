<template>
  <div class="auth-page">
    <div class="auth-card">
      <h2>注册</h2>
      <el-tabs v-model="regMode">
        <el-tab-pane label="邮箱注册" name="email">
          <el-form :model="form" :rules="emailRules" ref="formRef" label-position="top">
            <el-form-item label="用户名" prop="username">
              <el-input v-model="form.username" placeholder="请输入用户名" />
            </el-form-item>
            <el-form-item label="邮箱" prop="email">
              <div class="input-row">
                <el-input v-model="form.email" placeholder="请输入邮箱" />
                <el-button type="primary" :disabled="countdown>0" :loading="sendingCode" @click="sendEmailCode" class="input-btn">
                  {{ countdown>0 ? `${countdown}s` : '发送验证码' }}
                </el-button>
              </div>
            </el-form-item>
            <el-form-item label="验证码" prop="code">
              <el-input v-model="form.code" placeholder="6位验证码" maxlength="6" />
            </el-form-item>
            <el-form-item label="密码" prop="password">
              <el-input v-model="form.password" type="password" placeholder="至少8位" show-password />
            </el-form-item>
            <el-form-item label="确认密码" prop="password2">
              <el-input v-model="form.password2" type="password" placeholder="再次输入" show-password />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="loading" block @click="handleRegister">注册</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        <el-tab-pane label="手机注册" name="phone">
          <el-form :model="phoneForm" :rules="phoneRules" ref="phoneFormRef" label-position="top">
            <el-form-item label="手机号" prop="phone">
              <div class="input-row">
                <el-input v-model="phoneForm.phone" placeholder="11位手机号" maxlength="11" />
                <el-button type="primary" :disabled="phoneCountdown>0" :loading="sendingPhone" @click="sendPhoneCode" class="input-btn">
                  {{ phoneCountdown>0 ? `${phoneCountdown}s` : '发送验证码' }}
                </el-button>
              </div>
            </el-form-item>
            <el-form-item label="验证码" prop="code">
              <el-input v-model="phoneForm.code" placeholder="6位验证码" maxlength="6" />
            </el-form-item>
            <el-form-item label="密码" prop="password">
              <el-input v-model="phoneForm.password" type="password" placeholder="至少8位" show-password />
            </el-form-item>
            <el-form-item label="确认密码" prop="password2">
              <el-input v-model="phoneForm.password2" type="password" placeholder="再次输入" show-password />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="loading" block @click="handlePhoneRegister">注册</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
      <p class="switch-link">已有账号？<router-link to="/login">立即登录</router-link></p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import request from '@/api/request'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()
const regMode = ref('email')
const loading = ref(false)
const formRef = ref(null), phoneFormRef = ref(null)
const sendingCode = ref(false), countdown = ref(0)
const sendingPhone = ref(false), phoneCountdown = ref(0)

const form = reactive({ username: '', email: '', code: '', password: '', password2: '' })
const phoneForm = reactive({ phone: '', code: '', password: '', password2: '' })

const pwRule = [{ required: true, message: '请输入密码' }, { min: 8, message: '至少8位' }]
const pw2Rule = (f) => [{ required: true, message: '请再次输入' }, { validator: (_r, v, cb) => v !== f.password ? cb(new Error('两次密码不一致')) : cb() }]

const emailRules = {
  username: [{ required: true, message: '请输入用户名' }],
  email: [{ required: true, message: '请输入邮箱' }, { type: 'email', message: '格式不正确' }],
  code: [{ required: true, message: '请输入验证码' }],
  password: pwRule,
  password2: pw2Rule(form),
}
const phoneRules = {
  phone: [{ required: true, message: '请输入手机号' }, { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确' }],
  code: [{ required: true, message: '请输入验证码' }],
  password: pwRule,
  password2: pw2Rule(phoneForm),
}

async function sendEmailCode() {
  try { await formRef.value.validateField('email') } catch { return }
  sendingCode.value = true
  try {
    await request.post('/auth/send-code', { email: form.email })
    ElMessage.success('验证码已发送')
    countdown.value = 60; const t = setInterval(() => { countdown.value--; if (countdown.value <= 0) clearInterval(t) }, 1000)
  } catch (e) { ElMessage.error(e.response?.data?.data?.detail || '发送失败') }
  finally { sendingCode.value = false }
}

async function sendPhoneCode() {
  try { await phoneFormRef.value.validateField('phone') } catch { return }
  sendingPhone.value = true
  try {
    await request.post('/auth/send-sms-code', { phone: phoneForm.phone })
    ElMessage.success('验证码已发送')
    phoneCountdown.value = 60; const t = setInterval(() => { phoneCountdown.value--; if (phoneCountdown.value <= 0) clearInterval(t) }, 1000)
  } catch (e) { ElMessage.error(e.response?.data?.data?.detail || '发送失败') }
  finally { sendingPhone.value = false }
}

async function handleRegister() {
  const v = await formRef.value.validate().catch(() => false)
  if (!v) return; loading.value = true
  try {
    await authStore.register(form)
    ElMessage.success('注册成功'); router.push('/')
  } catch (e) {
    const d = e.response?.data?.data
    ElMessage.error(typeof d === 'object' ? Object.values(d).flat().join(', ') : '注册失败')
  } finally { loading.value = false }
}

async function handlePhoneRegister() {
  const v = await phoneFormRef.value.validate().catch(() => false)
  if (!v) return; loading.value = true
  try {
    const res = await request.post('/auth/phone-register', phoneForm)
    authStore.token = res.data.access; authStore.user = res.data.user
    localStorage.setItem('access_token', res.data.access); localStorage.setItem('refresh_token', res.data.refresh)
    ElMessage.success('注册成功'); router.push('/')
  } catch (e) {
    const d = e.response?.data?.data
    ElMessage.error(typeof d === 'object' ? Object.values(d).flat().join(', ') : '注册失败')
  } finally { loading.value = false }
}
</script>

<style scoped>
.auth-page { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: #f0f2f5; }
.auth-card { width: 430px; padding: 40px; background: #fff; border-radius: 8px; box-shadow: 0 2px 12px rgba(0,0,0,0.1); }
.auth-card h2 { text-align: center; margin-bottom: 16px; }
.input-row { display: flex; gap: 8px; }
.input-row .el-input { flex: 1; }
.input-btn { flex-shrink: 0; min-width: 110px; }
.switch-link { text-align: center; color: #999; margin-top: 8px; }
.switch-link a { color: #409eff; }
</style>
