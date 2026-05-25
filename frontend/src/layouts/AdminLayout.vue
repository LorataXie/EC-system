<!-- ============================================================ -->
<!-- 后台管理布局 - 管理端页面外壳                                     -->
<!-- 结构：深色侧边栏（菜单导航）+ 顶栏（用户信息 + 操作）+ 内容区        -->
<!-- ============================================================ -->
<template>
  <div class="admin-layout">
    <!-- ===== 深色侧边栏：固定宽度的管理菜单 ===== -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <h2>后台管理</h2>
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409eff"
      >
        <el-menu-item index="/admin">
          <el-icon><DataBoard /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/admin/users">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/products">
          <el-icon><Goods /></el-icon>
          <span>商品管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/categories">
          <el-icon><Folder /></el-icon>
          <span>分类管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/orders">
          <el-icon><Document /></el-icon>
          <span>订单管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/coupons">
          <el-icon><Ticket /></el-icon>
          <span>优惠券管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/analytics">
          <el-icon><DataAnalysis /></el-icon>
          <span>数据分析</span>
        </el-menu-item>
      </el-menu>
    </aside>

    <!-- ===== 右侧主区域 ===== -->
    <div class="main-area">
      <!-- 顶栏：当前用户 + 回首页 + 退出 -->
      <header class="top-bar">
        <span class="greeting">{{ authStore.user?.email }}</span>
        <el-button text @click="$router.push('/')">回首页</el-button>
        <el-button text @click="handleLogout">退出</el-button>
      </header>

      <!-- 内容区（子路由渲染位置） -->
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
// 管理端需要的图标组件（在此显式导入，避免全局注册未涵盖的情况）
import { DataBoard, User, Goods, Folder, Document, Ticket, DataAnalysis } from '@element-plus/icons-vue'

const route = useRoute()
const authStore = useAuthStore()

// 当前激活的菜单项（直接取当前路径）
const activeMenu = computed(() => route.path)

// 退出登录
async function handleLogout() {
  await authStore.logout()
  window.location.href = '/'
}
</script>

<style scoped>
/* ===== 整体左右布局 ===== */
.admin-layout { display: flex; min-height: 100vh; }
/* ===== 深色侧边栏 ===== */
.sidebar { width: 220px; background: #304156; color: #fff; flex-shrink: 0; }
.sidebar-header { padding: 20px; text-align: center; }
.sidebar-header h2 { color: #fff; font-size: 18px; margin: 0; }
/* ===== 右侧主区域 ===== */
.main-area { flex: 1; display: flex; flex-direction: column; }
/* 顶栏 */
.top-bar {
  height: 50px;
  background: #fff;
  border-bottom: 1px solid #eee;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 0 20px;
  gap: 12px;
}
.greeting { color: #666; }
/* 内容区 - 灰色背景，与 Element Plus 后台风格一致 */
.content { flex: 1; padding: 20px; background: #f0f2f5; overflow-y: auto; }
</style>
