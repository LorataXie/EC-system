<!-- ============================================================ -->
<!-- 结算/下单页 - 地址选择 + 优惠券 + 订单提交                          -->
<!-- 结构：左侧（地址 + 商品列表）+ 右侧汇总侧边栏                         -->
<!-- ============================================================ -->
<template>
  <div class="checkout-page">
    <h2>确认订单</h2>

    <div class="layout">
      <!-- ===== 左侧主内容 ===== -->
      <div class="main-content">
        <!-- 收货地址选择 -->
        <section class="address-section">
          <h3>收货地址</h3>
          <!-- 无地址时引导去添加 -->
          <div v-if="addresses.length === 0" class="address-empty">
            <p>暂无收货地址</p>
            <el-button type="primary" size="small" @click="$router.push('/profile/addresses')">去添加地址</el-button>
          </div>
          <!-- 地址列表：点击选中，高亮边框 -->
          <div v-else class="address-list">
            <div
              v-for="addr in addresses"
              :key="addr.id"
              class="address-item"
              :class="{ selected: selectedAddressId === addr.id }"
              @click="selectedAddressId = addr.id"
            >
              <div class="addr-header">
                <strong>{{ addr.recipient_name }}</strong>
                <span>{{ addr.phone }}</span>
                <!-- 默认地址标记 -->
                <el-tag v-if="addr.is_default" type="danger" size="small">默认</el-tag>
              </div>
              <p class="addr-text">{{ addr.state }} {{ addr.city }} {{ addr.address_line1 }}</p>
            </div>
          </div>
        </section>

        <!-- 商品确认清单 -->
        <section class="items-section">
          <h3>商品信息</h3>
          <!-- 购物车为空提示 -->
          <div v-if="!cartStore.cart.items?.length" class="cart-empty">
            <p>购物车为空</p>
            <el-button type="primary" size="small" @click="$router.push('/products')">去逛逛</el-button>
          </div>
          <!-- 商品行（可在此做最后调整） -->
          <CartItemRow
            v-for="item in cartStore.cart.items"
            :key="item.id"
            :item="item"
            @update="(id, qty) => cartStore.update(id, qty)"
            @remove="(id) => cartStore.remove(id)"
          />
        </section>
      </div>

      <!-- ===== 右侧汇总侧边栏（sticky 定位） ===== -->
      <aside class="summary-sidebar">
        <div class="summary-card">
          <p>商品数量：{{ cartStore.cart.items?.length || 0 }} 件</p>
          <p>商品总额：{{ formatPrice(cartStore.cart.total_amount || 0) }}</p>

          <!-- 优惠券选择器（使用时才显示） -->
          <div class="coupon-row" v-if="coupons.length > 0">
            <el-select
              v-model="selectedCouponId"
              placeholder="选择优惠券"
              clearable
              @change="onCouponChange"
              style="width:100%"
            >
              <!-- 优惠券标签：满X减Y -->
              <el-option v-for="c in coupons" :key="c.id" :label="couponLabel(c)" :value="c.id" />
            </el-select>
          </div>

          <!-- 优惠金额（仅当有优惠时显示） -->
          <p v-if="discountAmount > 0" class="discount">优惠：-{{ formatPrice(discountAmount) }}</p>

          <!-- 最终应付金额 -->
          <p class="final">应付：<strong>{{ formatPrice(finalAmount) }}</strong></p>

          <!-- 提交订单按钮 -->
          <el-button
            type="danger"
            size="large"
            block
            @click="handleCheckout"
            :loading="submitting"
            :disabled="!canCheckout"
          >
            提交订单
          </el-button>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '@/stores/cart'
import { useOrderStore } from '@/stores/order'
import { formatPrice } from '@/utils/format'
import CartItemRow from '@/components/cart/CartItemRow.vue'
import { getAddresses } from '@/api/address'
import { ElMessage } from 'element-plus'
import request from '@/api/request'

const router = useRouter()
const cartStore = useCartStore()
const orderStore = useOrderStore()

// 提交 loading 状态
const submitting = ref(false)
// 地址列表
const addresses = ref([])
// 可用优惠券列表
const coupons = ref([])
// 选中的地址 ID
const selectedAddressId = ref(null)
// 选中的优惠券 ID
const selectedCouponId = ref(null)
// 优惠金额
const discountAmount = ref(0)

// 最终应付 = 总额 - 优惠（不小于 0）
const finalAmount = computed(() => {
  return Math.max(0, (cartStore.cart.total_amount || 0) - discountAmount.value)
})

// 是否允许提交：购物车有商品 + 已选地址
const canCheckout = computed(() => {
  return cartStore.cart.items?.length > 0 && selectedAddressId.value
})

// 格式化优惠券展示标签
function couponLabel(c) {
  return `满${c.min_order_amount}减${c.discount_value}`
}

// 计算优惠金额：总额不满足门槛时不优惠
function calcDiscount(coupon, total) {
  if (!coupon) return 0
  if (total < coupon.min_order_amount) return 0
  return Math.min(coupon.discount_value, total)
}

// 优惠券选择变更 → 重新计算折扣金额
function onCouponChange(cid) {
  const c = coupons.value.find(x => x.id === cid)
  discountAmount.value = c ? calcDiscount(c, cartStore.cart.total_amount || 0) : 0
}

// 页面挂载：拉取购物车 + 地址列表 + 可用优惠券
onMounted(async () => {
  await cartStore.fetchCart()
  try {
    const [addrRes, couponRes] = await Promise.all([
      getAddresses(),
      request.get('/coupons/my', { params: { status: 'unused' } }),
    ])
    const addrList = addrRes.data?.results || addrRes.data || []
    addresses.value = addrList
    // 自动选中默认地址，无默认地址则选第一个
    const defaultAddr = addrList.find(a => a.is_default) || addrList[0]
    if (defaultAddr) selectedAddressId.value = defaultAddr.id
    coupons.value = couponRes.data?.results || couponRes.data || []
  } catch (e) {
    console.error('Failed to load checkout data')
  }
})

// 提交订单：校验 → 构建 payload → 调 store.place → 跳转订单列表
async function handleCheckout() {
  if (!cartStore.cart.items?.length) {
    ElMessage.warning('购物车为空')
    return
  }
  if (!selectedAddressId.value) {
    ElMessage.warning('请选择收货地址')
    return
  }
  try {
    submitting.value = true
    // 收集购物车中所有 item 的 ID（后端从购物车 item 创建订单）
    const itemIds = cartStore.cart.items.map(item => item.id)
    const payload = {
      address_id: selectedAddressId.value,
      item_ids: itemIds,
    }
    // 如果选了优惠券，一并传递
    if (selectedCouponId.value) payload.coupon_id = selectedCouponId.value
    await orderStore.place(payload)
    ElMessage.success('下单成功')
    router.push('/orders')
  } catch (e) {
    const detail = e?.response?.data?.data?.detail
    ElMessage.error(typeof detail === 'string' ? detail : '下单失败，请重试')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.checkout-page { max-width: 1100px; margin: 0 auto; }
h2 { margin-bottom: 20px; }
.layout { display: flex; gap: 24px; }
.main-content { flex: 1; min-width: 0; }
.summary-sidebar { width: 300px; flex-shrink: 0; }
.address-section, .items-section { background: #fff; padding: 20px; border-radius: 8px; margin-bottom: 16px; }
.address-section h3, .items-section h3 { margin-bottom: 12px; }
.address-empty, .cart-empty { text-align: center; padding: 24px; color: #999; }
.address-empty p, .cart-empty p { margin-bottom: 12px; }
/* 地址卡片 */
.address-item {
  border: 2px solid #eee; border-radius: 8px; padding: 12px; margin-bottom: 8px;
  cursor: pointer; transition: border-color .2s;
}
.address-item:hover { border-color: #409eff; }
/* 选中状态 */
.address-item.selected { border-color: #409eff; background: #ecf5ff; }
.addr-header { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
.addr-text { color: #666; font-size: 13px; }
/* 汇总卡片：sticky 定位跟随滚动 */
.summary-card { background: #fff; padding: 20px; border-radius: 8px; position: sticky; top: 80px; }
.summary-card p { margin-bottom: 8px; }
.coupon-row { margin: 8px 0; }
.discount { color: #67c23a; margin-bottom: 4px; }
.final { color: #e4393c; font-size: 18px; margin-top: 12px; }
</style>
