import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getCategories, getProducts, getProduct } from '@/api/products'

export const useProductStore = defineStore('product', () => {
  const categories = ref([])
  const products = ref([])
  const currentProduct = ref(null)
  const total = ref(0)
  const loading = ref(false)

  async function fetchCategories() {
    try {
      const res = await getCategories()
      categories.value = res.data || []
    } catch (e) {
      console.error('Failed to fetch categories')
    }
  }

  async function fetchProducts(params = {}) {
    loading.value = true
    try {
      const res = await getProducts(params)
      products.value = res.data?.results || []
      total.value = res.data?.count || 0
    } catch (e) {
      console.error('Failed to fetch products')
    } finally {
      loading.value = false
    }
  }

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
