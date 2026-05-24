<template>
  <div class="default-layout">
    <el-header class="app-header">
      <div class="header-left">
        <router-link to="/" class="logo">EC商城</router-link>
      </div>
      <div class="header-center">
        <el-input v-model="searchKeyword" placeholder="搜索商品..." clearable @keyup.enter="onSearch" class="search-input">
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
      <div class="header-right">
        <router-link to="/cart" class="cart-link">
          <el-badge :value="cartCount" :hidden="!cartCount">
            <el-icon :size="22"><ShoppingCart /></el-icon>
          </el-badge>
        </router-link>
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
                <el-dropdown-item v-if="authStore.isAdmin">
                  <router-link to="/admin">后台管理</router-link>
                </el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
        <template v-else>
          <el-button type="primary" size="small" @click="$router.push('/login')">登录</el-button>
          <el-button size="small" @click="$router.push('/register')">注册</el-button>
        </template>
      </div>
    </el-header>
    <main class="main-content">
      <router-view />
    </main>
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
const searchKeyword = ref('')
const cartCount = ref(0)

function onSearch() {
  if (searchKeyword.value.trim()) {
    router.push({ name: 'ProductList', query: { keyword: searchKeyword.value.trim() } })
  }
}

async function handleLogout() {
  await authStore.logout()
  router.push('/')
}
</script>

<style scoped>
.default-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
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
.header-center {
  flex: 1;
  max-width: 480px;
  margin: 0 24px;
}
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
.main-content {
  flex: 1;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  padding: 24px;
}
.app-footer {
  text-align: center;
  padding: 20px;
  color: #999;
  border-top: 1px solid #eee;
}
</style>
