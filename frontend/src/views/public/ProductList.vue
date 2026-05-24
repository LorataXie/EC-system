<template>
  <div class="product-list-page">
    <div class="layout">
      <aside class="sidebar">
        <ProductFilter :categories="productStore.categories" @change="handleFilterChange" />
      </aside>
      <main class="content">
        <div class="search-bar" v-if="keyword">
          搜索 "{{ keyword }}" 的结果，共 {{ productStore.total }} 件
        </div>
        <el-row :gutter="16">
          <el-col :span="6" v-for="product in productStore.products" :key="product.id">
            <ProductCard :product="product" />
          </el-col>
        </el-row>
        <AppPagination
          :total="productStore.total"
          :page-size-prop="pageSize"
          @page-change="handlePageChange"
          @size-change="handleSizeChange"
        />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useProductStore } from '@/stores/product'
import ProductCard from '@/components/product/ProductCard.vue'
import ProductFilter from '@/components/product/ProductFilter.vue'
import AppPagination from '@/components/common/AppPagination.vue'

const route = useRoute()
const productStore = useProductStore()

const keyword = ref(route.query.keyword || '')
const pageSize = ref(20)
const currentFilters = ref({})

function parseQueryToFilters(query) {
  const filters = {}
  if (query.category) filters.category = query.category
  if (query.min_price) filters.min_price = query.min_price
  if (query.max_price) filters.max_price = query.max_price
  if (query.sort) filters.sort = query.sort
  return filters
}

onMounted(async () => {
  await productStore.fetchCategories()
  keyword.value = route.query.keyword || ''
  currentFilters.value = parseQueryToFilters(route.query)
  loadProducts()
})

watch(() => route.query, (newQuery) => {
  keyword.value = newQuery.keyword || ''
  currentFilters.value = parseQueryToFilters(newQuery)
  loadProducts()
})

function buildParams(page = 1) {
  const params = { page, page_size: pageSize.value, ...currentFilters.value }
  if (keyword.value) params.keyword = keyword.value
  return params
}

async function loadProducts(page = 1) {
  await productStore.fetchProducts(buildParams(page))
}

function handleFilterChange(filters) {
  currentFilters.value = { ...currentFilters.value, ...filters }
  loadProducts(1)
}

function handlePageChange(page) {
  loadProducts(page)
}

function handleSizeChange(size) {
  pageSize.value = size
  loadProducts(1)
}
</script>

<style scoped>
.product-list-page { margin: 0 -24px; }
.layout { display: flex; gap: 20px; }
.sidebar { width: 240px; flex-shrink: 0; }
.content { flex: 1; }
.search-bar { padding: 12px 0; color: #666; font-size: 14px; }
.el-col { margin-bottom: 16px; }
</style>
