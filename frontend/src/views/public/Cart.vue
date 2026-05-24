<template>
  <div class="cart-page">
    <h2>购物车</h2>
    <div v-if="cartStore.cart.items && cartStore.cart.items.length > 0">
      <CartItemRow
        v-for="item in cartStore.cart.items"
        :key="item.id"
        :item="item"
        @update="(id, qty) => cartStore.update(id, qty)"
        @remove="(id) => cartStore.remove(id)"
      />
      <CartSummary
        :item-count="cartStore.cart.items.length"
        :total-amount="cartStore.cart.total_amount"
        @checkout="$router.push('/checkout')"
      />
    </div>
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

onMounted(() => {
  cartStore.fetchCart()
})
</script>

<style scoped>
.cart-page { background: #fff; padding: 24px; border-radius: 8px; }
h2 { margin-bottom: 20px; }
</style>
