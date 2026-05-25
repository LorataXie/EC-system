// ============================================================
// 应用入口文件 - Vue 应用初始化与全局配置
// ============================================================

// Vue 核心库
import { createApp } from 'vue'

// Pinia 状态管理
import { createPinia } from 'pinia'

// Element Plus UI 组件库及其样式
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

// Element Plus 中文语言包
import zhCn from 'element-plus/es/locale/lang/zh-cn'

// Element Plus 图标全集（按需注册为全局组件）
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

// 根组件
import App from './App.vue'

// 路由实例
import router from './router'

// 全局 SCSS 样式
import './assets/styles/global.scss'

// 创建 Vue 应用实例
const app = createApp(App)

// 全局错误处理器 - 捕获未处理的 Vue 运行时错误
app.config.errorHandler = (err, _instance, info) => {
  console.error('Vue Error:', err)
  console.error('Error Info:', info)
}

// 批量注册所有 Element Plus 图标为全局组件
// 这样在模板中可以直接使用 <el-icon><ComponentName /></el-icon>
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 安装 Pinia 状态管理
app.use(createPinia())

// 安装 Vue Router
app.use(router)

// 安装 Element Plus，并设置中文语言
app.use(ElementPlus, { locale: zhCn })

// 挂载应用到 #app DOM 节点
app.mount('#app')
