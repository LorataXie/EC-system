<template>
  <div>
    <h2>数据分析</h2>
    <div class="kpi-cards">
      <el-card><h3>{{ overview.revenue || '¥0' }}</h3><p>总销售额</p></el-card>
      <el-card><h3>{{ overview.orders || 0 }}</h3><p>订单量</p></el-card>
      <el-card><h3>{{ overview.users || 0 }}</h3><p>注册用户</p></el-card>
    </div>
    <el-row :gutter="16" style="margin-top:20px">
      <el-col :span="16">
        <el-card>
          <h4>销售趋势</h4>
          <v-chart :option="trendOption" style="height:300px" />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <h4>热销商品 Top10</h4>
          <v-chart :option="barOption" style="height:300px" />
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
import { getOverview, getSalesTrend, getHotProducts } from '@/api/admin/analytics'

use([CanvasRenderer, LineChart, BarChart, GridComponent, TooltipComponent, LegendComponent])

const overview = ref({})
const trendData = ref([])
const hotProducts = ref([])

const trendOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: trendData.value.map(t => t.period?.substring(0, 10)) },
  yAxis: { type: 'value' },
  series: [{ name: '销售额', type: 'line', data: trendData.value.map(t => t.total), smooth: true }],
}))

const barOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'value' },
  yAxis: { type: 'category', data: hotProducts.value.map(p => p.name).reverse() },
  series: [{ type: 'bar', data: (hotProducts.value.map(p => p.total_quantity || 0)).reverse() }],
}))

onMounted(async () => {
  try {
    const [ov, trend, hot] = await Promise.all([
      getOverview(), getSalesTrend(6), getHotProducts(10),
    ])
    overview.value = ov.data || {}
    trendData.value = trend.data || []
    hotProducts.value = hot.data || []
  } catch (e) {
    console.error('Analytics load failed', e)
  }
})
</script>

<style scoped>
h2 { margin-bottom: 20px; }
.kpi-cards { display: flex; gap: 16px; }
.kpi-cards .el-card { flex: 1; text-align: center; }
.kpi-cards h3 { font-size: 24px; color: #409eff; }
h4 { margin-bottom: 12px; }
</style>
