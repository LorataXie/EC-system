<template>
  <div>
    <h2>仪表盘</h2>
    <div class="kpi-cards">
      <el-card><h3>{{ kpis.revenue || '¥0' }}</h3><p>总销售额</p></el-card>
      <el-card><h3>{{ kpis.orders || 0 }}</h3><p>总订单数</p></el-card>
      <el-card><h3>{{ kpis.users || 0 }}</h3><p>注册用户</p></el-card>
      <el-card><h3>{{ kpis.products || 0 }}</h3><p>商品数量</p></el-card>
    </div>
    <el-row :gutter="16">
      <el-col :span="16">
        <el-card><h4>销售趋势</h4><v-chart :option="trendOption" style="height:300px" /></el-card>
      </el-col>
      <el-col :span="8">
        <el-card><h4>最近订单</h4>
          <div v-if="recentOrders.length === 0" class="placeholder-text">暂无订单</div>
          <div v-for="o in recentOrders" :key="o.id" class="recent-order" @click="$router.push(`/admin/orders/${o.id}`)" style="cursor:pointer; border-bottom:1px solid #eee; padding:8px 0">
            <p style="font-size:13px">{{ o.items?.[0]?.product_name || '订单' }} x{{ o.items?.length || 0 }}</p>
            <p style="color:#999;font-size:12px">{{ formatPrice(o.total_amount) }} · {{ formatDate(o.created_at) }}</p>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'

import { getOverview, getSalesTrend, getRecentOrders } from '@/api/admin/analytics'
import { formatPrice, formatDate } from '@/utils/format'

use([CanvasRenderer, LineChart, BarChart, GridComponent, TooltipComponent, LegendComponent])

const kpis = ref({})
const trendData = ref([])
const recentOrders = ref([])

const trendOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: trendData.value.map(t => t.period?.substring(0, 10)) },
  yAxis: { type: 'value' },
  series: [{ name: '销售额', type: 'line', data: trendData.value.map(t => t.total), smooth: true }],
}))

onMounted(async () => {
  try {
    const [kpiRes, trendRes, ordersRes] = await Promise.all([
      getOverview(),
      getSalesTrend(6),
      getRecentOrders(5),
    ])
    kpis.value = kpiRes.data || {}
    trendData.value = trendRes.data || []
    recentOrders.value = ordersRes.data || []
  } catch (e) {
    console.error('Failed to load dashboard')
  }
})
</script>

<style scoped>
h2 { margin-bottom: 20px; }
.kpi-cards { display: flex; gap: 16px; margin-bottom: 20px; }
.kpi-cards .el-card { flex: 1; text-align: center; }
.kpi-cards h3 { font-size: 24px; color: #409eff; }
h4 { margin-bottom: 12px; }
.placeholder-text { color: #999; padding: 20px 0; }
</style>
