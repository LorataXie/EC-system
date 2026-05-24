<template>
  <div class="page">
    <div class="header-row">
      <h2>消费统计</h2>
      <div class="controls">
        <el-radio-group v-model="period" @change="loadStats" size="small">
          <el-radio-button value="day">日</el-radio-button>
          <el-radio-button value="week">周</el-radio-button>
          <el-radio-button value="month">月</el-radio-button>
        </el-radio-group>
        <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始" end-placeholder="结束" @change="loadStats" size="small" style="margin-left:12px;width:240px" />
        <el-button size="small" @click="exportExcel" style="margin-left:8px">导出 Excel</el-button>
      </div>
    </div>
    <div class="stats-cards">
      <el-card><h3>{{ formatPrice(stats.total_spent||0) }}</h3><p>累计消费</p></el-card>
      <el-card><h3>{{ stats.order_count||0 }}</h3><p>订单总数</p></el-card>
      <el-card><h3>{{ avgOrderValue }}</h3><p>平均订单金额</p></el-card>
    </div>
    <div class="charts">
      <el-card>
        <h4>消费趋势</h4>
        <v-chart :option="trendOption" style="height:350px" />
      </el-card>
      <el-card>
        <h4>商品类别占比</h4>
        <v-chart :option="pieOption" style="height:350px" />
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, PieChart, LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent, TitleComponent } from 'echarts/components'
import { formatPrice } from '@/utils/format'
import request from '@/api/request'

use([CanvasRenderer, BarChart, PieChart, LineChart, GridComponent, TooltipComponent, LegendComponent, TitleComponent])

const stats = ref({})
const period = ref('month')
const dateRange = ref([])

const avgOrderValue = computed(() => {
  if (stats.value.order_count > 0) return formatPrice(stats.value.total_spent / stats.value.order_count)
  return '-'
})

const trendOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: (stats.value.trend||[]).map(t => t.period?.substring(0,10)) },
  yAxis: { type: 'value' },
  series: [
    { name: '消费金额', type: 'line', data: (stats.value.trend||[]).map(t => t.total), smooth: true, areaStyle:{opacity:0.1} },
    { name: '订单数', type: 'bar', data: (stats.value.trend||[]).map(t => t.count), yAxisIndex:1 },
  ],
  legend: { data:['消费金额','订单数'] },
}))

const pieOption = computed(() => ({
  tooltip: { trigger: 'item', formatter:'{b}: {c} ({d}%)' },
  series: [{
    type: 'pie', radius: ['40%','70%'],
    data: (stats.value.categories||[]).map(c => ({ name:c['items__product__category__name'], value:c.total })),
    label: { formatter:'{b}\n{d}%' },
  }],
}))

async function loadStats() {
  const params = { period: period.value }
  if (dateRange.value?.length===2) {
    params.start = dateRange.value[0].toISOString()
    params.end = dateRange.value[1].toISOString()
  }
  try {
    const res = await request.get('/profile/statistics', { params })
    stats.value = res.data || {}
  } catch(e) { console.error('Failed to load stats') }
}

function exportExcel() {
  const rows = [['周期','消费金额','订单数']]
  for (const t of (stats.value.trend||[])) {
    rows.push([t.period?.substring(0,10), t.total, t.count])
  }
  rows.push([])
  rows.push(['类别','消费金额'])
  for (const c of (stats.value.categories||[])) {
    rows.push([c['items__product__category__name'], c.total])
  }
  const csv = rows.map(r => r.map(v => `"${v??''}"`).join(',')).join('\n')
  const blob = new Blob(['﻿'+csv], {type:'text/csv;charset=utf-8'})
  const a = document.createElement('a'); a.href = URL.createObjectURL(blob)
  a.download = `消费明细_${new Date().toISOString().slice(0,10)}.csv`
  a.click()
}

onMounted(() => loadStats())
</script>

<style scoped>
.header-row { display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; }
.header-row h2 { margin:0; }
.controls { display:flex; align-items:center; }
.stats-cards { display:flex; gap:16px; margin-bottom:24px; }
.stats-cards .el-card { flex:1; text-align:center; }
.stats-cards h3 { font-size:24px; color:#409eff; }
.charts { display:flex; gap:16px; }
.charts .el-card { flex:1; }
.charts h4 { margin-bottom:12px; }
</style>
