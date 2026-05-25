<!-- ============================================================ -->
<!-- 消费统计页 - ECharts 图表 + 数据导出                                -->
<!-- 包含：统计卡片（累计/订单数/均值）+ 消费趋势图 + 类别饼图 + Excel导出     -->
<!-- ============================================================ -->
<template>
  <div class="page">
    <!-- ===== 页面头部：标题 + 筛选控件 ===== -->
    <div class="header-row">
      <h2>消费统计</h2>
      <div class="controls">
        <!-- 时间粒度切换：日 / 周 / 月 -->
        <el-radio-group v-model="period" @change="loadStats" size="small">
          <el-radio-button value="day">日</el-radio-button>
          <el-radio-button value="week">周</el-radio-button>
          <el-radio-button value="month">月</el-radio-button>
        </el-radio-group>

        <!-- 日期范围选择器 -->
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始"
          end-placeholder="结束"
          @change="loadStats"
          size="small"
          style="margin-left:12px;width:240px"
        />

        <!-- 导出按钮 -->
        <el-button size="small" @click="exportExcel" style="margin-left:8px">导出 Excel</el-button>
      </div>
    </div>

    <!-- ===== 统计概览卡片 ===== -->
    <div class="stats-cards">
      <el-card><h3>{{ formatPrice(stats.total_spent||0) }}</h3><p>累计消费</p></el-card>
      <el-card><h3>{{ stats.order_count||0 }}</h3><p>订单总数</p></el-card>
      <el-card><h3>{{ avgOrderValue }}</h3><p>平均订单金额</p></el-card>
    </div>

    <!-- ===== ECharts 图表 ===== -->
    <div class="charts">
      <!-- 消费趋势图：折线（金额）+ 柱状（订单数）混合图表 -->
      <el-card>
        <h4>消费趋势</h4>
        <v-chart :option="trendOption" style="height:350px" />
      </el-card>

      <!-- 商品类别消费占比饼图 -->
      <el-card>
        <h4>商品类别占比</h4>
        <v-chart :option="pieOption" style="height:350px" />
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
// vue-echarts 组件
import VChart from 'vue-echarts'
// ECharts 按需引入
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, PieChart, LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent, TitleComponent } from 'echarts/components'
import { formatPrice } from '@/utils/format'
import request from '@/api/request'

// 注册 ECharts 所需组件（按需引入，减小打包体积）
use([CanvasRenderer, BarChart, PieChart, LineChart, GridComponent, TooltipComponent, LegendComponent, TitleComponent])

// 统计数据
const stats = ref({})
// 时间粒度
const period = ref('month')
// 日期范围
const dateRange = ref([])

// 计算平均订单金额
const avgOrderValue = computed(() => {
  if (stats.value.order_count > 0) return formatPrice(stats.value.total_spent / stats.value.order_count)
  return '-'
})

// 消费趋势图配置（折线 + 柱状混合图，双 Y 轴）
const trendOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: (stats.value.trend || []).map(t => t.period?.substring(0, 10)) },
  yAxis: { type: 'value' },
  series: [
    // 消费金额（折线，带面积填充）
    { name: '消费金额', type: 'line', data: (stats.value.trend || []).map(t => t.total), smooth: true, areaStyle: { opacity: 0.1 } },
    // 订单数（柱状图，使用第2个 Y 轴）
    { name: '订单数', type: 'bar', data: (stats.value.trend || []).map(t => t.count), yAxisIndex: 1 },
  ],
  legend: { data: ['消费金额', '订单数'] },
}))

// 类别占比饼图配置（环形图）
const pieOption = computed(() => ({
  tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
  series: [{
    type: 'pie',
    radius: ['40%', '70%'], // 内半径 40%，形成环形效果
    data: (stats.value.categories || []).map(c => ({ name: c['items__product__category__name'], value: c.total })),
    label: { formatter: '{b}\n{d}%' },
  }],
}))

// 加载统计数据
async function loadStats() {
  const params = { period: period.value }
  // 如果选择了日期范围，附加 start / end 参数
  if (dateRange.value?.length === 2) {
    params.start = dateRange.value[0].toISOString()
    params.end = dateRange.value[1].toISOString()
  }
  try {
    const res = await request.get('/profile/statistics', { params })
    stats.value = res.data || {}
  } catch (e) {
    console.error('Failed to load stats')
  }
}

// 导出为 CSV 文件（以 Excel 兼容格式）
function exportExcel() {
  // 构建行数据（趋势明细）
  const rows = [['周期', '消费金额', '订单数']]
  for (const t of (stats.value.trend || [])) {
    rows.push([t.period?.substring(0, 10), t.total, t.count])
  }
  // 空行分隔
  rows.push([])
  // 类别汇总
  rows.push(['类别', '消费金额'])
  for (const c of (stats.value.categories || [])) {
    rows.push([c['items__product__category__name'], c.total])
  }
  // 生成 CSV 字符串
  const csv = rows.map(r => r.map(v => `"${v ?? ''}"`).join(',')).join('\n')
  // data: URI 避免 blob: URL 在 HTTP 下被阻止
  const a = document.createElement('a')
  a.href = 'data:text/csv;charset=utf-8,' + encodeURIComponent('﻿' + csv)
  a.download = `消费明细_${new Date().toISOString().slice(0, 10)}.csv`
  a.click()
}

// 挂载时首次加载
onMounted(() => loadStats())
</script>

<style scoped>
.header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.header-row h2 { margin: 0; }
.controls { display: flex; align-items: center; }
/* 统计卡片 */
.stats-cards { display: flex; gap: 16px; margin-bottom: 24px; }
.stats-cards .el-card { flex: 1; text-align: center; }
.stats-cards h3 { font-size: 24px; color: #409eff; }
/* 图表区域：左右并排 */
.charts { display: flex; gap: 16px; }
.charts .el-card { flex: 1; }
.charts h4 { margin-bottom: 12px; }
</style>
