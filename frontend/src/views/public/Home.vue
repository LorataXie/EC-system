<!-- ============================================================ -->
<!-- 首页 - 商城入口页                                                 -->
<!-- 结构：Hero 横幅 + 分类导航 + 精选商品列表                            -->
<!-- ============================================================ -->
<template>
  <div class="home-page">
    <!-- ===== Hero 横幅：欢迎语 + 开始购物按钮 ===== -->
    <section class="hero">
      <h1>欢迎来到 EC商城</h1>
      <p>发现好物，享受便捷购物体验</p>
      <el-button type="primary" size="large" @click="$router.push('/products')">开始购物</el-button>
    </section>

    <!-- ===== 商品分类卡片（仅在有分类数据时渲染） ===== -->
    <section class="categories" v-if="productStore.categories.length">
      <h3>商品分类</h3>
      <div class="category-grid">
        <!-- 点击卡片跳转商品列表页并携带分类过滤参数 -->
        <div
          v-for="cat in productStore.categories"
          :key="cat.id"
          class="category-card"
          @click="$router.push(`/products?category=${cat.id}`)"
        >
          <el-icon :size="28"><Folder /></el-icon>
          <span>{{ cat.name }}</span>
        </div>
      </div>
    </section>

    <!-- ===== 精选商品：4列网格布局，每行4个商品卡片 ===== -->
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

const productStore = useProductStore()

// 页面挂载时：拉取分类 + 按价格倒序拉取前8件精选商品
onMounted(async () => {
  await productStore.fetchCategories()
  await productStore.fetchProducts({ sort: '-price', page_size: 8 })
})
</script>

<style scoped>
/* Hero 区域：渐变色背景 */
.hero {
  text-align: center;
  padding: 60px 0;
  background: linear-gradient(135deg, #409eff, #36cfc9);
  color: #fff;
  border-radius: 12px;
  margin-bottom: 32px;
}
.hero h1 { font-size: 36px; margin-bottom: 12px; }
.hero p { font-size: 16px; margin-bottom: 24px; opacity: .9; }
/* 分类区域 */
.categories { margin-bottom: 32px; }
.categories h3, .featured h3 { margin-bottom: 16px; font-size: 20px; }
.category-grid { display: flex; gap: 16px; flex-wrap: wrap; }
.category-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
  cursor: pointer;
  min-width: 100px;
  transition: all .2s;
}
.category-card:hover { background: #e6f0ff; }
/* 商品列间距 */
.el-col { margin-bottom: 16px; }
</style>
