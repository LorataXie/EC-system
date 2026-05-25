<!-- ============================================================ -->
<!-- 订单详情页 - 订单状态 + 商品项 + 收货/物流 + 金额 + 操作 + 评价       -->
<!-- ============================================================ -->
<template>
  <div class="page" v-loading="loading">
    <div v-if="order">
      <!-- ===== 订单头部：标题 + 状态标签 ===== -->
      <div class="header-row">
        <h2>订单详情</h2>
        <el-tag :type="STATUS_COLORS[order.status]" size="large">{{ STATUS_MAP[order.status] }}</el-tag>
      </div>

      <!-- 订单编号 & 下单时间 -->
      <p class="meta">订单编号：{{ order.id }}</p>
      <p class="meta">下单时间：{{ formatDateTime(order.created_at) }}</p>

      <!-- ===== 订单商品表格 ===== -->
      <OrderItemTable :items="order.items" />

      <!-- ===== 信息卡片网格 ===== -->
      <div class="info-grid">
        <!-- 收货信息卡片 -->
        <div class="info-card" v-if="order.address_snapshot?.recipient_name">
          <h4>收货信息</h4>
          <p>{{ order.address_snapshot.recipient_name }} {{ order.address_snapshot.phone }}</p>
          <p class="addr-detail">
            {{ order.address_snapshot.state }}{{ order.address_snapshot.city }} {{ order.address_snapshot.address_line1 }}
          </p>
        </div>

        <!-- 物流信息卡片 -->
        <div class="info-card" v-if="order.tracking_number">
          <h4>物流信息</h4>
          <p>{{ order.shipping_method || '快递' }}</p>
          <p>单号：<strong>{{ order.tracking_number }}</strong></p>
          <p v-if="order.status==='shipped'">预计 2-4 天送达</p>
          <p v-if="order.status==='delivered'">已送达</p>
        </div>

        <!-- 金额明细卡片 -->
        <div class="info-card">
          <h4>金额明细</h4>
          <p>商品总额：{{ formatPrice(order.total_amount) }}</p>
          <p v-if="order.discount_amount > 0">优惠：-{{ formatPrice(order.discount_amount) }}</p>
          <p class="final">实付：<strong>{{ formatPrice((order.total_amount||0)-(order.discount_amount||0)) }}</strong></p>
        </div>
      </div>

      <!-- ===== 操作按钮（根据状态不同显示） ===== -->
      <!-- 待支付：支付 + 取消 -->
      <div class="actions" v-if="order.status === 'pending'">
        <el-button type="success" @click="doPay">立即支付</el-button>
        <el-button type="danger" @click="doCancel">取消订单</el-button>
      </div>
      <!-- 已发货：确认收货 -->
      <div class="actions" v-if="order.status === 'shipped'">
        <el-button type="primary" @click="doConfirm">确认收货</el-button>
      </div>

      <!-- ===== 已完成订单的评价区域 ===== -->
      <div class="review-section" v-if="order.status === 'completed'">
        <h3>商品评价</h3>
        <div v-for="item in order.items" :key="item.id" class="review-item">
          <p class="review-product">{{ item.product_name }} x{{ item.quantity }}</p>
          <!-- 已评价：展示评分和评论内容 -->
          <div v-if="item.reviewed">
            <el-rate :model-value="item.myReview?.rating||0" disabled show-score size="small" />
            <p class="review-comment">{{ item.myReview?.comment }}</p>
          </div>
          <!-- 未评价：展示评价表单 -->
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
// 订单状态映射常量
import { ORDER_STATUS as STATUS_MAP, ORDER_STATUS_COLORS as STATUS_COLORS } from '@/utils/constants'
import OrderItemTable from '@/components/order/OrderItemTable.vue'
import request from '@/api/request'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const orderStore = useOrderStore()

// 订单数据
const order = ref(null)
const loading = ref(true)

// 挂载时：获取订单详情 + 已有评价数据
onMounted(async () => {
  const data = await orderStore.fetchOrder(route.params.id)
  if (data) {
    // 为每个 item 初始化评价相关字段
    data.items = (data.items || []).map(i => ({ ...i, rating: 5, comment: '', reviewed: false }))
    try {
      // 拉取该订单已有的评价，回填到对应商品项
      const res = await request.get('/reviews', { params: { order_id: data.id } })
      const reviews = res.data?.results || res.data || []
      data.items = data.items.map(i => {
        const r = reviews.find(rv => rv.product === i.product)
        return r ? { ...i, reviewed: true, myReview: r } : i
      })
    } catch (e) {
      // 获取评价失败不影响页面展示
    }
    order.value = data
  }
  loading.value = false
})

// 支付操作
async function doPay() {
  await request.post(`/orders/${order.value.id}/pay`)
  ElMessage.success('支付成功')
  router.go(0)
}

// 取消订单：二次确认
async function doCancel() {
  await ElMessageBox.confirm('确定取消订单？')
  await request.post(`/orders/${order.value.id}/cancel`)
  ElMessage.success('已取消')
  router.go(0)
}

// 确认收货
async function doConfirm() {
  await request.post(`/orders/${order.value.id}/confirm-delivery`)
  ElMessage.success('已确认收货')
  router.go(0)
}

// 提交评价
async function submitReview(item) {
  try {
    await request.post('/reviews', {
      product: item.product,
      order: order.value.id,
      rating: item.rating,
      comment: item.comment,
    })
    ElMessage.success('评价提交成功')
    // 更新本地状态，切换为已评价展示
    item.reviewed = true
    item.myReview = { rating: item.rating, comment: item.comment }
  } catch (e) {
    ElMessage.error(e?.response?.data?.data?.detail || '评价失败')
  }
}
</script>

<style scoped>
.header-row { display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }
.header-row h2 { margin: 0; }
.meta { color: #666; margin-bottom: 4px; }
/* 信息卡片网格 */
.info-grid { display: flex; gap: 16px; margin-top: 20px; }
.info-card { flex: 1; padding: 16px; background: #f9f9f9; border-radius: 8px; }
.info-card h4 { margin-bottom: 8px; }
.addr-detail { color: #666; font-size: 13px; }
.final { color: #e4393c; font-size: 16px; margin-top: 8px; }
/* 操作按钮区 */
.actions { margin-top: 20px; display: flex; gap: 12px; }
/* 评价区域 */
.review-section { margin-top: 24px; }
.review-section h3 { margin-bottom: 16px; }
.review-item { padding: 12px; border: 1px solid #eee; border-radius: 8px; margin-bottom: 12px; }
.review-product { font-weight: 600; margin-bottom: 4px; }
.review-comment { color: #666; font-size: 13px; margin-top: 4px; }
</style>
