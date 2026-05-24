<template>
  <div class="cart-item-row">
    <div class="item-info">
      <p class="item-name">{{ item.product_name }}</p>
      <p class="item-price">{{ formatPrice(item.product_price) }}</p>
    </div>
    <el-input-number v-model="localQty" :min="1" :max="item.product_stock" size="small" @change="handleQtyChange" />
    <span class="subtotal">{{ formatPrice(item.subtotal) }}</span>
    <el-button type="danger" text @click="emit('remove', item.id)">
      <el-icon><Delete /></el-icon>
    </el-button>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { formatPrice } from '@/utils/format'

const props = defineProps({ item: { type: Object, required: true } })
const emit = defineEmits(['update', 'remove'])

const localQty = ref(props.item.quantity)

watch(() => props.item.quantity, (val) => { localQty.value = val })

function handleQtyChange(val) {
  emit('update', props.item.id, val)
}
</script>

<style scoped>
.cart-item-row { display: flex; align-items: center; gap: 12px; padding: 16px 0; border-bottom: 1px solid #eee; }
.item-info { flex: 1; }
.item-name { font-size: 14px; margin-bottom: 4px; }
.item-price { color: #e4393c; font-weight: 600; }
.subtotal { font-weight: 600; min-width: 80px; text-align: right; color: #e4393c; }
</style>
