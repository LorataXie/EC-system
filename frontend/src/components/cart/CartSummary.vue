<template>
  <div class="cart-summary">
    <div class="summary-row">
      <span>共 <strong>{{ itemCount }}</strong> 件商品</span>
      <span>合计：<strong class="total">{{ formatPrice(totalAmount) }}</strong></span>
    </div>
    <el-button type="danger" size="large" :disabled="itemCount === 0" @click="$emit('checkout')">
      去结算
    </el-button>
  </div>
</template>

<script setup>
import { formatPrice } from '@/utils/format'

defineProps({
  itemCount: { type: Number, default: 0 },
  totalAmount: { type: [Number, String], default: 0 },
})

defineEmits(['checkout'])
</script>

<style scoped>
.cart-summary { display: flex; align-items: center; justify-content: space-between; padding: 16px; background: #fff; border-radius: 8px; margin-top: 16px; }
.summary-row { display: flex; gap: 24px; }
.total { color: #e4393c; font-size: 20px; }
</style>
