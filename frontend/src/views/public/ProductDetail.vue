<!-- ============================================================ -->
<!-- 商品详情页 - 图片 + 信息 + 评价                                    -->
<!-- 结构：图片画廊 + 右侧信息（价格/库存/购买） + 详情描述 + 用户评价       -->
<!-- ============================================================ -->
<template>
  <div class="product-detail" v-loading="loading">
    <!-- 加载完成后显示内容 -->
    <div class="detail-layout" v-if="product">
      <!-- ===== 左侧：商品主图 ===== -->
      <div class="gallery">
        <img v-if="product.image" :src="product.image" class="main-image" />
        <!-- 无图片时的占位 -->
        <div v-else class="main-image-placeholder">
          <el-icon :size="60"><Picture /></el-icon>
        </div>
      </div>

      <!-- ===== 右侧：商品信息 ===== -->
      <div class="info">
        <h1 class="name">{{ product.name }}</h1>
        <!-- 价格区块 -->
        <div class="price-box">
          <span class="price">{{ formatPrice(product.price) }}</span>
        </div>
        <!-- 库存信息 -->
        <div class="meta-row">
          <span>库存：{{ product.stock }}</span>
        </div>
        <!-- 操作区：数量选择 + 加入购物车 + 立即购买 -->
        <div class="actions">
          <el-input-number v-model="quantity" :min="1" :max="product.stock" />
          <el-button type="primary" size="large" @click="addToCart">加入购物车</el-button>
          <el-button type="danger" size="large" @click="buyNow">立即购买</el-button>
        </div>
      </div>
    </div>

    <!-- ===== 商品详情描述（富文本） ===== -->
    <div class="description-section" v-if="product">
      <h3>商品详情</h3>
      <div class="description" v-html="product.description"></div>
    </div>

    <!-- ===== 用户评价区域 ===== -->
    <div class="reviews-section" v-if="product">
      <h3>用户评价 ({{ reviews.length }})</h3>
      <div v-if="reviews.length === 0" class="no-reviews">暂无评价</div>
      <!-- 评价卡片列表 -->
      <div v-for="rv in reviews" :key="rv.id" class="review-card">
        <div class="review-header">
          <span class="reviewer">{{ rv.user_name }}</span>
          <el-rate :model-value="rv.rating" disabled show-score size="small" />
          <span class="review-date">{{ formatDate(rv.created_at) }}</span>
        </div>
        <p class="review-text">{{ rv.comment }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useProductStore } from '@/stores/product'
import { useCartStore } from '@/stores/cart'
import { useAuthStore } from '@/stores/auth'
import { formatPrice, formatDate } from '@/utils/format'
import { ElMessage } from 'element-plus'
import request from '@/api/request'

const route = useRoute()
const router = useRouter()
const productStore = useProductStore()
const cartStore = useCartStore()
const authStore = useAuthStore()

// 商品详情数据
const product = ref(null)
// 评价列表
const reviews = ref([])
// 加载状态
const loading = ref(true)
// 购买数量
const quantity = ref(1)

// 页面挂载时并发请求：商品详情 + 评价列表
onMounted(async () => {
  const [productData, reviewData] = await Promise.all([
    productStore.fetchProduct(route.params.id),
    request.get('/reviews', { params: { product_id: route.params.id } }).then(r => r.data?.results || r.data || []).catch(() => []),
  ])
  if (productData) product.value = productData
  reviews.value = reviewData
  loading.value = false
})

// 加入购物车：先校验登录态，再调 store 添加商品
async function addToCart() {
  if (!product.value) return
  // 未登录则跳转登录页，登录后回到当前页
  if (!authStore.isAuthenticated) {
    ElMessage.warning('请先登录')
    router.push({ name: 'Login', query: { redirect: route.fullPath } })
    return
  }
  try {
    await cartStore.add(product.value.id, quantity.value)
    ElMessage.success(`已将 ${quantity.value} 件 ${product.value.name} 加入购物车`)
  } catch (e) {
    const msg = e?.response?.data?.detail || e?.response?.data?.data?.detail || e?.message || '添加失败，请重试'
    ElMessage.error(typeof msg === 'string' ? msg : '添加失败，请重试')
  }
}

// 立即购买：加入购物车后直接跳转购物车
async function buyNow() {
  if (!authStore.isAuthenticated) {
    ElMessage.warning('请先登录')
    router.push({ name: 'Login', query: { redirect: route.fullPath } })
    return
  }
  await addToCart()
  router.push('/cart')
}
</script>

<style scoped>
.product-detail { max-width: 1000px; margin: 0 auto; }
/* 上下布局 */
.detail-layout { margin-bottom: 32px; display: flex; gap: 32px; }
/* 左侧图片 */
.gallery { width: 400px; flex-shrink: 0; }
.main-image { width: 100%; max-height: 400px; object-fit: cover; border-radius: 8px; }
.main-image-placeholder {
  width: 100%; height: 300px;
  display: flex; align-items: center; justify-content: center;
  background: #f5f7fa; border-radius: 8px; color: #ccc;
}
/* 右侧信息 */
.info { flex: 1; }
.name { font-size: 22px; margin-bottom: 8px; }
.brand { color: #666; margin-bottom: 12px; }
/* 价格区块：红色背景 */
.price-box { background: #fef0f0; padding: 16px; border-radius: 8px; margin-bottom: 16px; }
.price { color: #e4393c; font-size: 28px; font-weight: 700; }
.meta-row { display: flex; gap: 24px; color: #666; font-size: 14px; margin-bottom: 20px; }
.actions { display: flex; gap: 12px; align-items: center; }
/* 商品描述 */
.description-section { background: #fff; padding: 24px; border-radius: 8px; }
.description-section h3 { margin-bottom: 16px; }
.description { color: #666; line-height: 1.8; }
/* 评价区域 */
.reviews-section { background: #fff; padding: 24px; border-radius: 8px; margin-top: 16px; }
.reviews-section h3 { margin-bottom: 16px; }
.no-reviews { color: #999; text-align: center; padding: 24px; }
.review-card { border-bottom: 1px solid #f0f0f0; padding: 14px 0; }
.review-card:last-child { border-bottom: none; }
.review-header { display: flex; align-items: center; gap: 12px; margin-bottom: 6px; }
.reviewer { font-weight: 600; color: #333; }
.review-date { color: #999; font-size: 12px; margin-left: auto; }
.review-text { color: #555; font-size: 14px; line-height: 1.6; }
</style>
