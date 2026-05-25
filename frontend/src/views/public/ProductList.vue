<!-- ============================================================ -->
<!-- 商品列表页 - 筛选 + 网格 + 分页                                     -->
<!-- 结构：左侧筛选边栏 + 右侧商品网格 + 底部分页                          -->
<!-- ============================================================ -->
<template>
  <div class="product-list-page">
    <div class="layout">
      <!-- ===== 左侧筛选边栏 ===== -->
      <aside class="sidebar">
        <ProductFilter :categories="productStore.categories" @change="handleFilterChange" />
      </aside>

      <!-- ===== 右侧内容：搜索结果提示 + 商品网格 + 分页 ===== -->
      <main class="content">
        <!-- 有搜索关键词时显示结果统计 -->
        <div class="search-bar" v-if="keyword">
          搜索 "{{ keyword }}" 的结果，共 {{ productStore.total }} 件
        </div>

        <!-- 商品网格：每行4个 -->
        <el-row :gutter="16">
          <el-col :span="6" v-for="product in productStore.products" :key="product.id">
            <ProductCard :product="product" />
          </el-col>
        </el-row>

        <!-- 分页组件 -->
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

// 搜索关键词（来自路由 query）
const keyword = ref(route.query.keyword || '')
// 每页条数
const pageSize = ref(20)
// 当前筛选条件集合
const currentFilters = ref({})

// 将路由 query 参数解析为筛选条件对象
function parseQueryToFilters(query) {
  const filters = {}
  if (query.category) filters.category = query.category
  if (query.min_price) filters.min_price = query.min_price
  if (query.max_price) filters.max_price = query.max_price
  if (query.sort) filters.sort = query.sort
  return filters
}

// 页面挂载：加载分类 + 首次加载商品
onMounted(async () => {
  await productStore.fetchCategories()
  keyword.value = route.query.keyword || ''
  currentFilters.value = parseQueryToFilters(route.query)
  loadProducts()
})

// 监听路由 query 变化（同一页面内切换筛选条件时触发）
watch(() => route.query, (newQuery) => {
  keyword.value = newQuery.keyword || ''
  currentFilters.value = parseQueryToFilters(newQuery)
  loadProducts()
})

// 构建 API 请求参数
function buildParams(page = 1) {
  const params = { page, page_size: pageSize.value, ...currentFilters.value }
  if (keyword.value) params.keyword = keyword.value
  return params
}

// 加载商品数据
async function loadProducts(page = 1) {
  await productStore.fetchProducts(buildParams(page))
}

// 筛选条件变化时 → 重置到第1页
function handleFilterChange(filters) {
  currentFilters.value = { ...currentFilters.value, ...filters }
  loadProducts(1)
}

// 翻页
function handlePageChange(page) {
  loadProducts(page)
}

// 切换每页条数 → 重置到第1页
function handleSizeChange(size) {
  pageSize.value = size
  loadProducts(1)
}
</script>

<style scoped>
/* 去除外层 padding 约束，让列表全宽 */
.product-list-page { margin: 0 -24px; }
.layout { display: flex; gap: 20px; }
/* 左侧筛选栏 */
.sidebar { width: 240px; flex-shrink: 0; }
/* 右侧内容区 */
.content { flex: 1; }
.search-bar { padding: 12px 0; color: #666; font-size: 14px; }
.el-col { margin-bottom: 16px; }
</style>
