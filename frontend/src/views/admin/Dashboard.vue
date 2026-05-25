<template>
  <div class="dashboard-container">
    <h2 class="page-title">控制台概览</h2>

    <div class="stat-cards">
      <div class="stat-card blue">
        <div class="icon">💰</div>
        <div class="info">
          <p class="label">总销售额</p>
          <p class="value">¥{{ stats.total_sales }}</p>
        </div>
      </div>

      <div class="stat-card green">
        <div class="icon">📦</div>
        <div class="info">
          <p class="label">总订单</p>
          <p class="value">{{ stats.total_orders }}</p>
        </div>
      </div>

      <div class="stat-card purple">
        <div class="icon">👥</div>
        <div class="info">
          <p class="label">总用户</p>
          <p class="value">{{ stats.total_users }}</p>
        </div>
      </div>

      <div class="stat-card orange">
        <div class="icon">📊</div>
        <div class="info">
          <p class="label">总商品</p>
          <p class="value">{{ stats.total_products }}</p>
        </div>
      </div>
    </div>

    <div class="chart-wrapper">
      <h3>销售趋势</h3>
      <div class="chart-box">
        <v-chart :option="chartOption" autoresize />
      </div>
    </div>

    <div class="recent-orders">
      <h3>最近订单</h3>
      <div class="table-box">
        <el-table :data="recentOrders" border stripe>
          <el-table-column prop="id" label="订单号" />
          <el-table-column prop="user" label="用户" />
          <el-table-column prop="total_price" label="金额" />
          <el-table-column prop="status" label="状态" />
          <el-table-column prop="created_at" label="时间" />
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  GridComponent
} from 'echarts/components'

use([
  CanvasRenderer,
  LineChart,
  TitleComponent,
  TooltipComponent,
  GridComponent
])

const stats = ref({
  total_sales: 0,
  total_orders: 0,
  total_users: 0,
  total_products: 0
})
const recentOrders = ref([])
const chartOption = ref({})

onMounted(() => {
  chartOption.value = {
    tooltip: {},
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: ['1日', '2日', '3日', '4日', '5日', '6日', '7日']
    },
    yAxis: { type: 'value' },
    series: [
      {
        type: 'line',
        data: [120, 230, 224, 218, 200, 240, 270]
      }
    ]
  }
})
</script>

<style scoped>
.dashboard-container {
  padding: 28px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #2d3a4f;
  margin-bottom: 24px;
  text-align: center;
}

.stat-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 24px;
  border-radius: 16px;
  color: white;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
  transition: 0.3s;
}
.stat-card:hover {
  transform: translateY(-4px);
}

.blue {
  background: #3b82f6;
}
.green {
  background: #10b981;
}
.purple {
  background: #8b5cf6;
}
.orange {
  background: #f59e0b;
}

.icon {
  font-size: 32px;
  margin-right: 18px;
}

.info .label {
  font-size: 14px;
  opacity: 0.9;
  margin: 0;
}
.info .value {
  font-size: 22px;
  font-weight: bold;
  margin: 4px 0 0;
}

.chart-wrapper,
.recent-orders {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  margin-bottom: 24px;
}

.chart-box {
  height: 360px;
}

.table-box {
  margin-top: 12px;
}

h3 {
  font-size: 18px;
  color: #333;
  margin-bottom: 16px;
  font-weight: 600;
}
</style>
