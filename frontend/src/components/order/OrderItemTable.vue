<template>
  <el-table :data="items" stripe>
    <el-table-column prop="product_name" label="商品名称" />
    <el-table-column prop="price" label="单价" width="120">
      <template #default="{ row }">{{ formatPrice(row.price) }}</template>
    </el-table-column>
    <el-table-column prop="quantity" label="数量" width="80" />
    <el-table-column label="小计" width="120">
      <template #default="{ row }">{{ formatPrice(row.subtotal) }}</template>
    </el-table-column>
  </el-table>
</template>

<script setup>
import { formatPrice } from '@/utils/format'

defineProps({ items: { type: Array, default: () => [] } })
</script>
