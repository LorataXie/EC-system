<template>
  <div>
    <div class="page-header">
      <h2>商品管理</h2>
      <el-button type="primary" @click="$router.push('/admin/products/create')">新增商品</el-button>
    </div>
    <el-table :data="products" v-loading="loading" stripe>
      <el-table-column prop="name" label="商品名称" />
      <el-table-column label="分类" width="120">
        <template #default="{ row }">{{ row.category_name }}</template>
      </el-table-column>
      <el-table-column label="价格" width="100">
        <template #default="{ row }">{{ formatPrice(row.price) }}</template>
      </el-table-column>
      <el-table-column prop="stock" label="库存" width="80" />
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button size="small" @click="$router.push(`/admin/products/${row.id}/edit`)">编辑</el-button>
          <el-popconfirm title="确定删除？" @confirm="handleDelete(row.id)">
            <template #reference>
              <el-button size="small" type="danger">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { formatPrice } from '@/utils/format'
import request from '@/api/request'
import { ElMessage } from 'element-plus'

const products = ref([])
const loading = ref(false)

onMounted(() => loadProducts())

async function loadProducts() {
  loading.value = true
  try {
    const res = await request.get('/admin/products', { params: { page_size: 100 } })
    products.value = res.data?.results || res.data || []
  } catch (e) {
    console.error('Failed to load products')
  } finally {
    loading.value = false
  }
}

async function handleDelete(id) {
  try {
    await request.delete(`/admin/products/${id}`)
    ElMessage.success('已删除')
    loadProducts()
  } catch (e) {
    ElMessage.error('删除失败')
  }
}
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.page-header h2 { margin: 0; }
</style>
