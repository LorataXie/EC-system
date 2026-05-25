<template>
  <div class="cart-page">
    <h2>购物车</h2>

    <div v-if="cartStore.cart.items && cartStore.cart.items.length > 0">
      <div v-for="item in cartStore.cart.items" :key="item.id" class="cart-item">

        <div class="left-part">
          <img :src="item.product.image" class="p-img" />
          <span class="p-name">{{ item.product.name }}</span>
        </div>

        <CartItemRow
            :item="item"
            @update="(id, qty) => cartStore.update(id, qty)"
            @remove="(id) => cartStore.remove(id)"
        />

      </div>

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
onMounted(() => cartStore.fetchCart())
</script>

<style scoped>
.cart-page {
  background: #fafbfc;
  padding: 30px;
  border-radius: 16px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  max-width: 1100px;
  margin: 0 auto;
}

h2 {
  margin-bottom: 24px;
  font-size: 24px;
  color: #2c3e50;
}

.cart-item {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
  padding: 16px 20px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}

.left-part {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-right: auto;
}

.p-img {
  width: 55px;
  height: 55px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid #eee;
}

.p-name {
  font-size: 15px;
  font-weight: 500;
  color: #2c3e50;
}
</style>
