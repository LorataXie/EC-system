<template>
  <div>
    <div class="page-header">
      <h2>优惠券管理</h2>
      <div>
        <el-button type="success" @click="openIssueDialog">批量发放</el-button>
        <el-button type="primary" @click="$router.push('/admin/coupons/create')">创建单张</el-button>
      </div>
    </div>
    <el-table :data="coupons" v-loading="loading" stripe>
      <el-table-column label="用户" width="130">
        <template #default="{ row }">{{ row.user_email || '未发放' }}</template>
      </el-table-column>
      <el-table-column label="类型" width="80">
        <template #default="{ row }">{{ COUPON_TYPES[row.type] || row.type }}</template>
      </el-table-column>
      <el-table-column prop="discount_value" label="优惠值" width="70" />
      <el-table-column prop="min_order_amount" label="最低金额" width="90" />
      <el-table-column label="有效期" width="180">
        <template #default="{ row }">{{ formatDate(row.start_time) }} ~ {{ formatDate(row.end_time) }}</template>
      </el-table-column>
      <el-table-column label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.status === 'unused' ? 'success' : row.status === 'used' ? 'info' : 'danger'" size="small">
            {{ row.status === 'unused' ? '未使用' : row.status === 'used' ? '已使用' : '已过期' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="80">
        <template #default="{ row }">
          <el-popconfirm title="确定删除？" @confirm="handleDelete(row.id)">
            <template #reference>
              <el-button size="small" type="danger">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="issueVisible" title="批量发放优惠券给用户" width="500px">
      <el-form :model="issueForm" label-width="100px">
        <el-form-item label="减免金额">
          <el-input-number v-model="issueForm.discount_value" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item label="最低金额">
          <el-input-number v-model="issueForm.min_order_amount" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item label="开始时间">
          <el-date-picker v-model="issueForm.start_time" type="datetime" />
        </el-form-item>
        <el-form-item label="结束时间">
          <el-date-picker v-model="issueForm.end_time" type="datetime" />
        </el-form-item>
        <el-form-item label="筛选用户">
          <el-checkbox v-model="issueForm.filter_vip" @change="loadTargetUsers">VIP用户</el-checkbox>
          <el-checkbox v-model="issueForm.filter_purchased" @change="loadTargetUsers" style="margin-left:12px">有过消费</el-checkbox>
        </el-form-item>
        <el-form-item label="最低消费额">
          <el-input-number v-model="issueForm.filter_spent" :min="0" :precision="0" @change="loadTargetUsers" />
        </el-form-item>
        <el-form-item label="已选用户">
          <span>{{ issueForm.user_ids.length }} 人</span>
        </el-form-item>
        <el-form-item label="目标用户">
          <div class="user-list" v-loading="loadingUsers">
            <el-checkbox-group v-model="issueForm.user_ids">
              <div v-for="u in targetUsers" :key="u.id" class="user-row">
                <el-checkbox :value="u.id">
                  {{ u.email }} <el-tag v-if="u.is_vip" size="small" type="warning" style="margin-left:4px">VIP</el-tag>
                </el-checkbox>
              </div>
            </el-checkbox-group>
            <el-empty v-if="!targetUsers.length" description="无匹配用户" :image-size="40" />
          </div>
        </el-form-item>
        <el-form-item label="每人数量">
          <el-input-number v-model="issueForm.count_per_user" :min="1" :max="10" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="issueVisible = false">取消</el-button>
        <el-button type="primary" :loading="issuing" @click="handleIssue">确认发放</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { COUPON_TYPES } from '@/utils/constants'
import { formatDate } from '@/utils/format'
import request from '@/api/request'
import { ElMessage } from 'element-plus'

const coupons = ref([])
const loading = ref(false)
const issueVisible = ref(false)
const issuing = ref(false)

const issueForm = reactive({
  type: 'full_reduction', discount_value: 20, min_order_amount: 100,
  start_time: '', end_time: '', user_ids: [], filter_vip: false,
  filter_purchased: false, filter_spent: null, count_per_user: 1,
})
const targetUsers = ref([])
const loadingUsers = ref(false)

onMounted(() => loadCoupons())

async function loadCoupons() {
  loading.value = true
  try {
    const res = await request.get('/admin/coupons')
    coupons.value = res.data?.results || res.data || []
  } catch (e) {
    console.error('Failed to load coupons')
  } finally {
    loading.value = false
  }
}

function openIssueDialog() {
  issueForm.start_time = new Date().toISOString().slice(0, 16)
  issueForm.end_time = new Date(Date.now() + 90*86400000).toISOString().slice(0, 16)
  issueForm.user_ids = []
  issueForm.filter_vip = false
  issueForm.filter_purchased = false
  issueForm.filter_spent = null
  issueVisible.value = true
  loadTargetUsers()
}

async function loadTargetUsers() {
  loadingUsers.value = true
  try {
    const params = {}
    if (issueForm.filter_vip) params.is_vip = 'true'
    if (issueForm.filter_purchased) params.has_orders = 'true'
    if (issueForm.filter_spent) params.min_spent = issueForm.filter_spent
    const res = await request.get('/admin/users/filter-targets', { params })
    targetUsers.value = res.data || []
  } catch (e) {
    console.error('Failed to load users')
  } finally {
    loadingUsers.value = false
  }
}

async function handleIssue() {
  if (!issueForm.user_ids.length) { ElMessage.warning('请选择目标用户'); return }
  issuing.value = true
  try {
    await request.post('/admin/coupons/issue', {
      type: issueForm.type,
      discount_value: issueForm.discount_value,
      min_order_amount: issueForm.min_order_amount,
      start_time: issueForm.start_time,
      end_time: issueForm.end_time,
      user_ids: issueForm.user_ids,
      count_per_user: issueForm.count_per_user,
    })
    ElMessage.success(`已向 ${ids.length} 位用户各发放 ${issueForm.count_per_user} 张优惠券`)
    issueVisible.value = false
    loadCoupons()
  } catch (e) {
    ElMessage.error('发放失败')
  } finally {
    issuing.value = false
  }
}

async function handleDelete(id) {
  try {
    await request.delete(`/admin/coupons/${id}`)
    ElMessage.success('已删除')
    loadCoupons()
  } catch (e) {
    ElMessage.error('删除失败')
  }
}
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.page-header h2 { margin: 0; }
.user-list { max-height: 200px; overflow-y: auto; border: 1px solid #eee; border-radius: 4px; padding: 8px; }
.user-row { padding: 4px 0; }
</style>
