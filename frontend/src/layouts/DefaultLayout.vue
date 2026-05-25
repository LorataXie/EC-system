<!-- ============================================================ -->
<!-- 默认商城布局 - 公开页面外壳                                      -->
<!-- 结构：页头（Logo + 搜索栏 + 购物车 + 用户下拉）+ 主体 + 页脚       -->
<!-- ============================================================ -->
<template>
  <div class="default-layout">
    <!-- ===== 页头：固定在顶部 ===== -->
    <el-header class="app-header">
      <!-- 左侧：Logo，点击回首页 -->
      <div class="header-left">
        <router-link to="/" class="logo">EC商城</router-link>
      </div>

      <!-- 中间：全局搜索栏，回车跳转商品列表页 -->
      <div class="header-center">
        <el-input v-model="searchKeyword" placeholder="搜索商品..." clearable @keyup.enter="onSearch" class="search-input">
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>

      <!-- 右侧：购物车 + 用户操作 -->
      <div class="header-right">
        <!-- 购物车入口，带数量徽标 -->
        <router-link to="/cart" class="cart-link">
          <el-badge :value="cartCount" :hidden="!cartCount">
            <el-icon :size="22"><ShoppingCart /></el-icon>
          </el-badge>
        </router-link>

        <!-- 已登录：用户下拉菜单 -->
        <template v-if="authStore.isAuthenticated">
          <el-dropdown>
            <span class="user-name">{{ authStore.user?.email }}</span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>
                  <router-link to="/profile">个人中心</router-link>
                </el-dropdown-item>
                <el-dropdown-item>
                  <router-link to="/orders">我的订单</router-link>
                </el-dropdown-item>
                <!-- 管理员可见：后台管理入口 -->
                <el-dropdown-item v-if="authStore.isAdmin">
                  <router-link to="/admin">后台管理</router-link>
                </el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>

        <!-- 未登录：登录 / 注册按钮 -->
        <template v-else>
          <el-button type="primary" size="small" @click="$router.push('/login')">登录</el-button>
          <el-button size="small" @click="$router.push('/register')">注册</el-button>
        </template>
      </div>
    </el-header>

    <!-- ===== 主体内容区域（子路由渲染位置） ===== -->
    <main class="main-content">
      <router-view />
    </main>

    <!-- ===== 页脚 ===== -->
    <el-footer class="app-footer">
      <p>&copy; 2026 EC商城 - 电商系统</p>
    </el-footer>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
// 搜索关键词（双向绑定到输入框）
const searchKeyword = ref('')
// 购物车数量（用于徽标，如需实时更新可在 onMounted 中 fetchCart）
const cartCount = ref(0)

// 按下回车或点击搜索 → 携带 keyword 参数跳转到商品列表
function onSearch() {
  if (searchKeyword.value.trim()) {
    router.push({ name: 'ProductList', query: { keyword: searchKeyword.value.trim() } })
  }
}

// 退出登录 → 调用 store 清除 token → 刷新页面回到首页
async function handleLogout() {
  await authStore.logout()
  window.location.href = '/'
}
</script>

<style scoped>
/* ===== 布局 ===== */
.default-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
/* ===== 页头 ===== */
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 60px;
  background: #fff;
  border-bottom: 1px solid #eee;
  position: sticky;
  top: 0;
  z-index: 100;
}
.logo {
  font-size: 22px;
  font-weight: 700;
  color: #409eff;
  text-decoration: none;
}
/* 搜索栏 */
.header-center {
  flex: 1;
  max-width: 480px;
  margin: 0 24px;
}
/* 右侧操作区 */
.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}
.cart-link {
  color: #333;
  text-decoration: none;
}
.user-name {
  cursor: pointer;
  color: #333;
}
/* ===== 主内容区 ===== */
.main-content {
  flex: 1;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  padding: 24px;
}
/* ===== 页脚 ===== */
.app-footer {
  text-align: center;
  padding: 20px;
  color: #999;
  border-top: 1px solid #eee;
}
</style>
