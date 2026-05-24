<template>
  <div class="product-filter">
    <div class="filter-section">
      <h4>商品分类</h4>
      <el-tree
        :data="categories"
        :props="{ label: 'name', children: 'children' }"
        node-key="id"
        :default-expand-all="false"
        @node-click="handleCategoryClick"
        highlight-current
      />
    </div>
    <div class="filter-section">
      <h4>价格区间</h4>
      <el-slider
        v-model="priceRange"
        range
        :min="0"
        :max="10000"
        :step="100"
        @change="handlePriceChange"
      />
      <span class="price-label">{{ priceRange[0] }} - {{ priceRange[1] }}</span>
    </div>
    <div class="filter-section">
      <h4>排序</h4>
      <el-radio-group v-model="sortBy" @change="handleSortChange">
        <el-radio value="">默认</el-radio>
        <el-radio value="-sales_count">销量优先</el-radio>
        <el-radio value="price">价格从低到高</el-radio>
        <el-radio value="-price">价格从高到低</el-radio>
      </el-radio-group>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  categories: { type: Array, default: () => [] },
})

const emit = defineEmits(['change'])

const sortBy = ref('')
const priceRange = ref([0, 10000])

function handleCategoryClick(node) {
  emit('change', { category: node.id })
}

function handlePriceChange() {
  emit('change', { min_price: priceRange.value[0], max_price: priceRange.value[1] })
}

function handleSortChange(val) {
  emit('change', { sort: val })
}
</script>

<style scoped>
.product-filter { background: #fff; border-radius: 8px; padding: 16px; }
.filter-section { margin-bottom: 20px; }
.filter-section h4 { margin-bottom: 10px; font-size: 14px; color: #333; }
.price-label { color: #999; font-size: 12px; }
.el-radio-group { display: flex; flex-direction: column; gap: 8px; }
</style>
