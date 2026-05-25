<template>
  <div class="home-page">
    <div class="notice-bar">
      <el-carousel
          direction="vertical"
          :interval="3500"
          arrow="never"
          height="28px"
          class="notice-carousel"
      >
        <el-carousel-item>🎉 新品上线，全场低至 7 折！</el-carousel-item>
        <el-carousel-item>🚚 满 99 元免运费，速来选购</el-carousel-item>
        <el-carousel-item>🎁 新用户注册立减 15 元</el-carousel-item>
        <el-carousel-item>⭐ 欢迎来到 EC 商城，祝您购物愉快</el-carousel-item>
      </el-carousel>
    </div>

    <section class="hero">
      <h1>欢迎来到 EC商城</h1>
      <p>发现好物，享受便捷购物体验</p>
      <el-button type="primary" size="large" @click="$router.push('/products')">开始购物</el-button>
    </section>

    <section class="categories" v-if="productStore.categories.length">
      <h3>商品分类</h3>
      <div class="category-grid">
        <div v-for="cat in productStore.categories" :key="cat.id" class="category-card" @click="$router.push(`/products?category=${cat.id}`)">
          <el-icon :size="28"><Folder /></el-icon>
          <span>{{ cat.name }}</span>
        </div>
      </div>
    </section>

    <section class="featured">
      <h3>精选商品</h3>
      <el-row :gutter="16">
        <el-col :span="6" v-for="product in productStore.products" :key="product.id">
          <ProductCard :product="product" />
        </el-col>
      </el-row>
    </section>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useProductStore } from '@/stores/product'
import ProductCard from '@/components/product/ProductCard.vue'
import { Folder } from '@element-plus/icons-vue'

const productStore = useProductStore()

onMounted(async () => {
  await productStore.fetchCategories()
  await productStore.fetchProducts({ sort: '-price', page_size: 8 })
})
</script>

<style scoped>
.home-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

/* 🔔 消息轮播样式 */
.notice-bar {
  background: #fff7cc;
  color: #e67c00;
  border-radius: 8px;
  height: 28px;
  line-height: 28px;
  text-align: center;
  font-size: 13px;
  margin-bottom: 16px;
  overflow: hidden;
}
.notice-carousel {
  height: 28px !important;
}
.notice-carousel :deep(.el-carousel__container) {
  height: 28px !important;
}
.notice-carousel :deep(.el-carousel__item) {
  height: 28px !important;
  line-height: 28px !important;
}

.hero {
  text-align: center;
  padding: 80px 0;
  background: linear-gradient(135deg, #409eff, #36cfc9);
  color: #fff;
  border-radius: 16px;
  margin-bottom: 40px;
  box-shadow: 0 4px 20px rgba(64, 158, 255, 0.2);
}

.hero h1 {
  font-size: 40px;
  margin-bottom: 16px;
  font-weight: 700;
}

.hero p {
  font-size: 18px;
  margin-bottom: 28px;
  opacity: .95;
}

.categories {
  margin-bottom: 44px;
}

.categories h3,
.featured h3 {
  margin-bottom: 20px;
  font-size: 22px;
  font-weight: 600;
  color: #333;
}

.category-grid {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.category-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 24px 20px;
  background: #fff;
  border-radius: 12px;
  cursor: pointer;
  min-width: 110px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  border: 1px solid #f0f0f0;
}

.category-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
  background: #e6f0ff;
  border-color: #d0e7ff;
}

.el-col {
  margin-bottom: 20px;
}

.featured {
  margin-bottom: 40px;
}
</style>
