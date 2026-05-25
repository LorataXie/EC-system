<!-- ============================================================ -->
<!-- 购物车页 - 商品列表 + 汇总结算                                     -->
<!-- 结构：购物车商品行 + 汇总栏（总数/总价/去结算）                       -->
<!-- ============================================================ -->
<template>
  <div class="cart-page">
    <h2>购物车</h2>

    <!-- 有商品时：渲染商品行 + 汇总 -->
    <div v-if="cartStore.cart.items && cartStore.cart.items.length > 0">
      <!-- 购物车商品行：支持修改数量、移除 -->
      <CartItemRow
        v-for="item in cartStore.cart.items"
        :key="item.id"
        :item="item"
        @update="(id, qty) => cartStore.update(id, qty)"
        @remove="(id) => cartStore.remove(id)"
      />
      <!-- 汇总栏：显示总数和总价，点击跳转结算页 -->
      <CartSummary
        :item-count="cartStore.cart.items.length"
        :total-amount="cartStore.cart.total_amount"
        @checkout="$router.push('/checkout')"
      />
    </div>

    <!-- 空购物车：占位提示 + 跳转商品页 -->
    <el-empty v-else description="购物车空空如也">
      <el-button type="primary" @click="$router.push('/products')">去逛逛</el-button>
    </el-empty>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useCartStore } from '@/stores/cart'
import CartItemRow from '@/components/cart/CartItemRow.vue'
import CartSummary from '@/components/cart/CartSummary.vue'

const cartStore = useCartStore()

// 页面挂载时从服务器拉取购物车数据
onMounted(() => {
  cartStore.fetchCart()
})
</script>

<style scoped>
.cart-page { background: #fff; padding: 24px; border-radius: 8px; }
h2 { margin-bottom: 20px; }
</style>
