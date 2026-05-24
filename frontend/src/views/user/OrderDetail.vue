<template>
  <div class="page" v-loading="loading">
    <div v-if="order">
      <div class="header-row">
        <h2>订单详情</h2>
        <el-tag :type="STATUS_COLORS[order.status]" size="large">{{ STATUS_MAP[order.status] }}</el-tag>
      </div>
      <p class="meta">订单编号：{{ order.id }}</p>
      <p class="meta">下单时间：{{ formatDateTime(order.created_at) }}</p>

      <OrderItemTable :items="order.items" />

      <div class="info-grid">
        <div class="info-card" v-if="order.address_snapshot?.recipient_name">
          <h4>收货信息</h4>
          <p>{{ order.address_snapshot.recipient_name }} {{ order.address_snapshot.phone }}</p>
          <p class="addr-detail">{{ order.address_snapshot.state }}{{ order.address_snapshot.city }} {{ order.address_snapshot.address_line1 }}</p>
        </div>
        <div class="info-card" v-if="order.tracking_number">
          <h4>物流信息</h4>
          <p>{{ order.shipping_method || '快递' }}</p>
          <p>单号：<strong>{{ order.tracking_number }}</strong></p>
          <p v-if="order.status==='shipped'">预计 2-4 天送达</p>
          <p v-if="order.status==='delivered'">已送达</p>
        </div>
        <div class="info-card">
          <h4>金额明细</h4>
          <p>商品总额：{{ formatPrice(order.total_amount) }}</p>
          <p v-if="order.discount_amount > 0">优惠：-{{ formatPrice(order.discount_amount) }}</p>
          <p class="final">实付：<strong>{{ formatPrice((order.total_amount||0)-(order.discount_amount||0)) }}</strong></p>
        </div>
      </div>

      <div class="actions" v-if="order.status === 'pending'">
        <el-button type="success" @click="doPay">立即支付</el-button>
        <el-button type="danger" @click="doCancel">取消订单</el-button>
      </div>
      <div class="actions" v-if="order.status === 'shipped'">
        <el-button type="primary" @click="doConfirm">确认收货</el-button>
      </div>

      <div class="review-section" v-if="order.status === 'completed'">
        <h3>商品评价</h3>
        <div v-for="item in order.items" :key="item.id" class="review-item">
          <p class="review-product">{{ item.product_name }} x{{ item.quantity }}</p>
          <div v-if="item.reviewed">
            <el-rate :model-value="item.myReview?.rating||0" disabled show-score size="small" />
            <p class="review-comment">{{ item.myReview?.comment }}</p>
          </div>
          <div v-else class="review-form">
            <el-rate v-model="item.rating" show-score size="small" />
            <el-input v-model="item.comment" placeholder="写下评价..." type="textarea" :rows="2" style="margin-top:4px" />
            <el-button type="primary" size="small" style="margin-top:4px" @click="submitReview(item)">提交评价</el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useOrderStore } from '@/stores/order'
import { formatPrice, formatDateTime } from '@/utils/format'
import { ORDER_STATUS as STATUS_MAP, ORDER_STATUS_COLORS as STATUS_COLORS } from '@/utils/constants'
import OrderItemTable from '@/components/order/OrderItemTable.vue'
import request from '@/api/request'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute(); const router = useRouter()
const orderStore = useOrderStore()
const order = ref(null); const loading = ref(true)

onMounted(async () => {
  const data = await orderStore.fetchOrder(route.params.id)
  if (data) {
    data.items = (data.items||[]).map(i => ({...i, rating:5, comment:'', reviewed:false}))
    try {
      const res = await request.get('/reviews', { params: { order_id: data.id } })
      const reviews = res.data?.results||res.data||[]
      data.items = data.items.map(i => {
        const r = reviews.find(rv => rv.product === i.product)
        return r ? {...i, reviewed:true, myReview:r} : i
      })
    } catch(e){}
    order.value = data
  }
  loading.value = false
})

async function doPay() {
  await request.post(`/orders/${order.value.id}/pay`)
  ElMessage.success('支付成功'); router.go(0)
}
async function doCancel() {
  await ElMessageBox.confirm('确定取消订单？')
  await request.post(`/orders/${order.value.id}/cancel`)
  ElMessage.success('已取消'); router.go(0)
}
async function doConfirm() {
  await request.post(`/orders/${order.value.id}/confirm-delivery`)
  ElMessage.success('已确认收货'); router.go(0)
}
async function submitReview(item) {
  try {
    await request.post('/reviews', { product:item.product, order:order.value.id, rating:item.rating, comment:item.comment })
    ElMessage.success('评价提交成功'); item.reviewed=true; item.myReview={rating:item.rating,comment:item.comment}
  } catch(e) { ElMessage.error(e?.response?.data?.data?.detail||'评价失败') }
}
</script>

<style scoped>
.header-row { display:flex; align-items:center; gap:12px; margin-bottom:8px; }
.header-row h2 { margin:0; }
.meta { color:#666; margin-bottom:4px; }
.info-grid { display:flex; gap:16px; margin-top:20px; }
.info-card { flex:1; padding:16px; background:#f9f9f9; border-radius:8px; }
.info-card h4 { margin-bottom:8px; }
.addr-detail { color:#666; font-size:13px; }
.final { color:#e4393c; font-size:16px; margin-top:8px; }
.actions { margin-top:20px; display:flex; gap:12px; }
.review-section { margin-top:24px; }
.review-section h3 { margin-bottom:16px; }
.review-item { padding:12px; border:1px solid #eee; border-radius:8px; margin-bottom:12px; }
.review-product { font-weight:600; margin-bottom:4px; }
.review-comment { color:#666; font-size:13px; margin-top:4px; }
</style>
