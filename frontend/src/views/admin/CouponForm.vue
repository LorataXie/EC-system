<template>
  <div>
    <h2>创建优惠券</h2>
    <el-form :model="form" ref="formRef" label-width="120px" class="coupon-form">
      <el-form-item label="减免金额" required>
        <el-input-number v-model="form.discount_value" :min="0" :precision="2" />
        <span class="hint">元</span>
      </el-form-item>
      <el-form-item label="最低订单金额">
        <el-input-number v-model="form.min_order_amount" :min="0" :precision="2" />
      </el-form-item>
      <el-form-item label="开始时间" required>
        <el-date-picker v-model="form.start_time" type="datetime" />
      </el-form-item>
      <el-form-item label="结束时间" required>
        <el-date-picker v-model="form.end_time" type="datetime" />
      </el-form-item>
      <el-form-item label="状态">
        <el-select v-model="form.status">
          <el-option label="未使用" value="unused" />
          <el-option label="已使用" value="used" />
          <el-option label="已过期" value="expired" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" :loading="saving" @click="handleSave">创建</el-button>
        <el-button @click="$router.back()">取消</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { COUPON_TYPES } from '@/utils/constants'
import request from '@/api/request'
import { ElMessage } from 'element-plus'

const router = useRouter()
const formRef = ref(null)
const saving = ref(false)

const form = reactive({
  type: 'full_reduction',
  discount_value: 0,
  min_order_amount: 0,
  start_time: '',
  end_time: '',
  status: 'unused',
  user: null,
})

async function handleSave() {
  saving.value = true
  try {
    await request.post('/admin/coupons', form)
    ElMessage.success('优惠券已创建')
    router.push('/admin/coupons')
  } catch (e) {
    ElMessage.error('创建失败')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
h2 { margin-bottom: 20px; }
.coupon-form { max-width: 560px; background: #fff; padding: 24px; border-radius: 8px; }
.hint { color: #999; margin-left: 8px; }
</style>
