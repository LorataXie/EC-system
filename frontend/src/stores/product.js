// ============================================================
// 商品状态管理 (Pinia Store)
// 管理：分类列表、商品列表（分页）、当前商品详情、加载状态
// ============================================================

import { defineStore } from 'pinia'
import { ref } from 'vue'
// 商品 API 方法
import { getCategories, getProducts, getProduct } from '@/api/products'

export const useProductStore = defineStore('product', () => {
  // 商品分类列表
  const categories = ref([])
  // 商品列表（当前页数据）
  const products = ref([])
  // 当前查看的商品详情
  const currentProduct = ref(null)
  // 商品总条数（用于分页组件）
  const total = ref(0)
  // 加载状态标识
  const loading = ref(false)

  // 获取全部分类
  async function fetchCategories() {
    try {
      const res = await getCategories()
      categories.value = res.data || []
    } catch (e) {
      console.error('Failed to fetch categories')
    }
  }

  // 分页获取商品列表，支持传入筛选参数
  async function fetchProducts(params = {}) {
    loading.value = true
    try {
      const res = await getProducts(params)
      // 接口返回分页结构：{ results: [...], count: 总数 }
      products.value = res.data?.results || []
      total.value = res.data?.count || 0
    } catch (e) {
      console.error('Failed to fetch products')
    } finally {
      loading.value = false
    }
  }

  // 获取单个商品详情
  async function fetchProduct(id) {
    try {
      const res = await getProduct(id)
      currentProduct.value = res.data
      return res.data
    } catch (e) {
      console.error('Failed to fetch product')
      return null
    }
  }

  return { categories, products, currentProduct, total, loading, fetchCategories, fetchProducts, fetchProduct }
})
