<template>
  <div class="user-layout">
    <el-header class="app-header">
      <div class="header-left">
        <router-link to="/" class="logo">EC商城</router-link>
      </div>
      <div class="header-right">
        <router-link to="/cart">
          <el-icon :size="22"><ShoppingCart /></el-icon>
        </router-link>
        <el-dropdown>
          <span class="user-name">{{ authStore.user?.email }}</span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item><router-link to="/">回到首页</router-link></el-dropdown-item>
              <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>
    <div class="user-body">
      <aside class="sidebar">
        <el-menu :default-active="activeMenu" router>
          <el-menu-item index="/profile">
            <el-icon><User /></el-icon>
            <span>个人信息</span>
          </el-menu-item>
          <el-menu-item index="/profile/addresses">
            <el-icon><Location /></el-icon>
            <span>收货地址</span>
          </el-menu-item>
          <el-menu-item index="/orders">
            <el-icon><Document /></el-icon>
            <span>我的订单</span>
          </el-menu-item>
          <el-menu-item index="/profile/statistics">
            <el-icon><DataAnalysis /></el-icon>
            <span>消费统计</span>
          </el-menu-item>
        </el-menu>
      </aside>
      <main class="content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const authStore = useAuthStore()
const activeMenu = computed(() => {
  if (route.path.startsWith('/orders')) return '/orders'
  return route.path
})

async function handleLogout() {
  await authStore.logout()
}
</script>

<style scoped>
.user-layout { min-height: 100vh; display: flex; flex-direction: column; }
.app-header { display: flex; align-items: center; justify-content: space-between; height: 60px; background: #fff; border-bottom: 1px solid #eee; padding: 0 24px; }
.logo { font-size: 22px; font-weight: 700; color: #409eff; text-decoration: none; }
.header-right { display: flex; align-items: center; gap: 16px; }
.user-name { cursor: pointer; }
.user-body { display: flex; flex: 1; max-width: 1200px; margin: 0 auto; width: 100%; }
.sidebar { width: 200px; border-right: 1px solid #eee; padding-top: 16px; }
.content { flex: 1; padding: 24px; }
</style>
