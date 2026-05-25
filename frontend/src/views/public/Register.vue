<!-- ============================================================ -->
<!-- 注册页 - 邮箱验证码注册 + 手机验证码注册                             -->
<!-- 两种注册方式通过 el-tabs 切换                                      -->
<!-- ============================================================ -->
<template>
  <div class="auth-page">
    <div class="auth-card">
      <h2>注册</h2>

      <!-- 注册方式切换 Tab -->
      <el-tabs v-model="regMode">
        <!-- ===== 邮箱注册面板 ===== -->
        <el-tab-pane label="邮箱注册" name="email">
          <el-form :model="form" :rules="emailRules" ref="formRef" label-position="top">
            <!-- 用户名 -->
            <el-form-item label="用户名" prop="username">
              <el-input v-model="form.username" placeholder="请输入用户名" />
            </el-form-item>

            <!-- 邮箱 + 发送验证码按钮（横向排列） -->
            <el-form-item label="邮箱" prop="email">
              <div class="input-row">
                <el-input v-model="form.email" placeholder="请输入邮箱" />
                <el-button
                  type="primary"
                  :disabled="countdown>0"
                  :loading="sendingCode"
                  @click="sendEmailCode"
                  class="input-btn"
                >
                  {{ countdown>0 ? `${countdown}s` : '发送验证码' }}
                </el-button>
              </div>
            </el-form-item>

            <!-- 验证码 -->
            <el-form-item label="验证码" prop="code">
              <el-input v-model="form.code" placeholder="6位验证码" maxlength="6" />
            </el-form-item>

            <!-- 密码 -->
            <el-form-item label="密码" prop="password">
              <el-input v-model="form.password" type="password" placeholder="至少8位" show-password />
            </el-form-item>

            <!-- 确认密码 -->
            <el-form-item label="确认密码" prop="password2">
              <el-input v-model="form.password2" type="password" placeholder="再次输入" show-password />
            </el-form-item>

            <el-form-item>
              <el-button type="primary" :loading="loading" block @click="handleRegister">注册</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- ===== 手机注册面板 ===== -->
        <el-tab-pane label="手机注册" name="phone">
          <el-form :model="phoneForm" :rules="phoneRules" ref="phoneFormRef" label-position="top">
            <!-- 手机号 + 发送验证码按钮 -->
            <el-form-item label="手机号" prop="phone">
              <div class="input-row">
                <el-input v-model="phoneForm.phone" placeholder="11位手机号" maxlength="11" />
                <el-button
                  type="primary"
                  :disabled="phoneCountdown>0"
                  :loading="sendingPhone"
                  @click="sendPhoneCode"
                  class="input-btn"
                >
                  {{ phoneCountdown>0 ? `${phoneCountdown}s` : '发送验证码' }}
                </el-button>
              </div>
            </el-form-item>

            <!-- 验证码 -->
            <el-form-item label="验证码" prop="code">
              <el-input v-model="phoneForm.code" placeholder="6位验证码" maxlength="6" />
            </el-form-item>

            <!-- 密码 -->
            <el-form-item label="密码" prop="password">
              <el-input v-model="phoneForm.password" type="password" placeholder="至少8位" show-password />
            </el-form-item>

            <!-- 确认密码 -->
            <el-form-item label="确认密码" prop="password2">
              <el-input v-model="phoneForm.password2" type="password" placeholder="再次输入" show-password />
            </el-form-item>

            <el-form-item>
              <el-button type="primary" :loading="loading" block @click="handlePhoneRegister">注册</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>

      <!-- 底部链接：跳转登录 -->
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

// 当前注册方式：email / phone
const regMode = ref('email')
// 注册提交 loading
const loading = ref(false)

// 邮箱表单 ref
const formRef = ref(null)
// 手机表单 ref
const phoneFormRef = ref(null)

// 邮箱验证码：发送 loading + 倒计时
const sendingCode = ref(false)
const countdown = ref(0)

// 手机验证码：发送 loading + 倒计时
const sendingPhone = ref(false)
const phoneCountdown = ref(0)

// 邮箱注册表单数据
const form = reactive({ username: '', email: '', code: '', password: '', password2: '' })
// 手机注册表单数据
const phoneForm = reactive({ phone: '', code: '', password: '', password2: '' })

// 密码通用验证规则
const pwRule = [{ required: true, message: '请输入密码' }, { min: 8, message: '至少8位' }]
// 确认密码验证规则（闭包引用对应的 form 对象，确保密码一致性校验）
const pw2Rule = (f) => [
  { required: true, message: '请再次输入' },
  { validator: (_r, v, cb) => v !== f.password ? cb(new Error('两次密码不一致')) : cb() },
]

// 邮箱表单验证规则
const emailRules = {
  username: [{ required: true, message: '请输入用户名' }],
  email: [{ required: true, message: '请输入邮箱' }, { type: 'email', message: '格式不正确' }],
  code: [{ required: true, message: '请输入验证码' }],
  password: pwRule,
  password2: pw2Rule(form),
}

// 手机表单验证规则
const phoneRules = {
  phone: [{ required: true, message: '请输入手机号' }, { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确' }],
  code: [{ required: true, message: '请输入验证码' }],
  password: pwRule,
  password2: pw2Rule(phoneForm),
}

// 发送邮箱验证码：先验邮箱字段 → 调接口 → 启动60秒倒计时
async function sendEmailCode() {
  try { await formRef.value.validateField('email') } catch { return }
  sendingCode.value = true
  try {
    await request.post('/auth/send-code', { email: form.email })
    ElMessage.success('验证码已发送')
    countdown.value = 60
    const t = setInterval(() => { countdown.value--; if (countdown.value <= 0) clearInterval(t) }, 1000)
  } catch (e) {
    ElMessage.error(e.response?.data?.data?.detail || '发送失败')
  } finally {
    sendingCode.value = false
  }
}

// 发送手机验证码：先验手机字段 → 调接口 → 启动60秒倒计时
async function sendPhoneCode() {
  try { await phoneFormRef.value.validateField('phone') } catch { return }
  sendingPhone.value = true
  try {
    await request.post('/auth/send-sms-code', { phone: phoneForm.phone })
    ElMessage.success('验证码已发送')
    phoneCountdown.value = 60
    const t = setInterval(() => { phoneCountdown.value--; if (phoneCountdown.value <= 0) clearInterval(t) }, 1000)
  } catch (e) {
    ElMessage.error(e.response?.data?.data?.detail || '发送失败')
  } finally {
    sendingPhone.value = false
  }
}

// 邮箱注册：表单验证 → store.register → 跳转首页
async function handleRegister() {
  const v = await formRef.value.validate().catch(() => false)
  if (!v) return
  loading.value = true
  try {
    await authStore.register(form)
    ElMessage.success('注册成功')
    router.push('/')
  } catch (e) {
    const d = e.response?.data?.data
    ElMessage.error(typeof d === 'object' ? Object.values(d).flat().join(', ') : '注册失败')
  } finally {
    loading.value = false
  }
}

// 手机注册：表单验证 → 调手机注册接口 → 手动写入 token → 跳转首页
async function handlePhoneRegister() {
  const v = await phoneFormRef.value.validate().catch(() => false)
  if (!v) return
  loading.value = true
  try {
    const res = await request.post('/auth/phone-register', phoneForm)
    authStore.token = res.data.access
    authStore.user = res.data.user
    localStorage.setItem('access_token', res.data.access)
    localStorage.setItem('refresh_token', res.data.refresh)
    ElMessage.success('注册成功')
    router.push('/')
  } catch (e) {
    const d = e.response?.data?.data
    ElMessage.error(typeof d === 'object' ? Object.values(d).flat().join(', ') : '注册失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* 同登录页卡片布局 */
.auth-page { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: #f0f2f5; }
.auth-card { width: 430px; padding: 40px; background: #fff; border-radius: 8px; box-shadow: 0 2px 12px rgba(0,0,0,0.1); }
.auth-card h2 { text-align: center; margin-bottom: 16px; }
/* 输入框 + 按钮横向排列 */
.input-row { display: flex; gap: 8px; }
.input-row .el-input { flex: 1; }
.input-btn { flex-shrink: 0; min-width: 110px; }
.switch-link { text-align: center; color: #999; margin-top: 8px; }
.switch-link a { color: #409eff; }
</style>
