<template>
  <div class="product-card" @click="$router.push(`/products/${product.id}`)">
    <div class="product-image-wrapper">
      <img v-if="product.image" :src="product.image" class="product-image" />
      <div v-else class="product-image-placeholder">
        <el-icon :size="40"><Picture /></el-icon>
      </div>
    </div>
    <div class="product-info">
      <p class="product-name">{{ product.name }}</p>
      <div class="product-price-row">
        <span class="price">{{ formatPrice(product.price) }}</span>
        <span class="sales" v-if="product.sales_count">已售 {{ product.sales_count }}</span>
        <el-rate v-if="product.rating_avg > 0" :model-value="Number(product.rating_avg)" disabled show-score size="small" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { formatPrice } from '@/utils/format'

defineProps({
  product: { type: Object, required: true },
})
</script>

<style scoped>
.product-card { border: 1px solid #eee; border-radius: 8px; overflow: hidden; cursor: pointer; transition: all .2s; background: #fff; }
.product-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.1); transform: translateY(-2px); }
.product-image-wrapper { width: 100%; height: 180px; overflow: hidden; }
.product-image { width: 100%; height: 100%; object-fit: cover; }
.product-image-placeholder { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; background: #f5f7fa; color: #ccc; }
.product-info { padding: 12px; }
.product-name { font-size: 14px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; margin-bottom: 8px; }
.product-price-row { display: flex; align-items: baseline; gap: 8px; }
.price { color: #e4393c; font-size: 18px; font-weight: 600; }
</style>
