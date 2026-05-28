<template>
  <div class="ur-wrap">
    <div class="ur-head">
      <span class="ur-dot">&#9679;</span> 用户活跃排行榜
      <span class="ur-sub">Top 10</span>
    </div>
    <div ref="chartDom" class="ur-body"></div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({ users: { type: Array, required: true } })
const chartDom = ref(null)
let myChart = null

function makeOption(list) {
  const has = list && list.length > 0
  const reversed = has ? [...list].reverse() : []
  const names = has ? reversed.map(u => u.name.length > 8 ? u.name.slice(0,7) + '…' : u.name) : []
  const values = has ? reversed.map(u => u.value) : []

  return {
    tooltip: {
      trigger: 'axis', axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(20,30,60,0.95)',
      borderColor: 'rgba(100,255,218,0.3)',
      textStyle: { color: '#e0e6ff', fontSize: 12 }
    },
    grid: { left: 80, right: 30, top: 10, bottom: 20 },
    xAxis: {
      type: 'value', minInterval: 1,
      splitLine: { lineStyle: { color: 'rgba(100,255,218,0.05)' } },
      axisLabel: { color: '#8892b0', fontSize: 9 }
    },
    yAxis: {
      type: 'category', data: names,
      axisLine: { lineStyle: { color: 'rgba(100,255,218,0.2)' } },
      axisTick: { show: false },
      axisLabel: { color: '#e0e6ff', fontSize: 10 }
    },
    series: [{
      type: 'bar', data: values, barWidth: 14,
      itemStyle: {
        borderRadius: [0, 6, 6, 0],
        color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
          { offset: 0, color: 'rgba(100,255,218,0.5)' },
          { offset: 1, color: 'rgba(100,255,218,0.9)' }
        ])
      },
      label: { show: true, position: 'right', color: '#8892b0', fontSize: 9 }
    }]
  }
}

function render() {
  const dom = chartDom.value
  if (!dom) return
  if (dom.clientHeight === 0) {
    dom.style.height = '200px'
  }
  if (!myChart) {
    myChart = echarts.init(dom)
  }
  myChart.setOption(makeOption(props.users))
}

onMounted(() => {
  nextTick(() => render())
  window.addEventListener('resize', () => myChart?.resize())
})

watch(() => props.users, () => render(), { deep: true })

onUnmounted(() => {
  myChart?.dispose()
  myChart = null
})
</script>

<style scoped>
.ur-wrap { display: flex; flex-direction: column; height: 100%; }
.ur-head {
  font-size: 14px; font-weight: 600; color: #64ffda;
  padding-bottom: 10px; border-bottom: 1px solid rgba(100,255,218,0.15);
  flex-shrink: 0;
  display: flex; align-items: center;
}
.ur-dot { font-size: 10px; margin-right: 4px; }
.ur-sub { font-size: 11px; font-weight: 400; color: #8892b0; margin-left: auto; }
.ur-body { flex: 1; min-height: 180px; width: 100%; }
</style>
