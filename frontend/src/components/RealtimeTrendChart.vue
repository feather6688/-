<!--
RealtimeTrendChart.vue — 实时情绪波动趋势（最近 2.5 分钟，30 个采样点）
用于展示当前观众情绪的波动变化，区别于累计趋势图
-->
<template>
  <div class="rt-wrap">
    <div class="rt-head">
      <span class="rt-dot"></span>
      <span class="rt-title">实时情绪波动</span>
      <span class="rt-sub">近2.5分钟 · 每5秒采样</span>
    </div>
    <div ref="chartDom" class="rt-body"></div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  data: { type: Array, required: true }
  // [{time, positive, neutral, negative}, ...] 最多30个点
})

const chartDom = ref(null)
let chart = null

function buildOption(raw) {
  const times = raw.map(d => d.time)
  const pos = raw.map(d => d.positive)
  const neu = raw.map(d => d.neutral)
  const neg = raw.map(d => d.negative)

  return {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(8,12,30,0.95)',
      borderColor: 'rgba(100,255,218,0.25)',
      textStyle: { color: '#e0e6ff', fontSize: 11 }
    },
    legend: {
      bottom: 0,
      textStyle: { color: '#8892b0', fontSize: 10 },
      data: ['正向', '中性', '负向'],
      itemWidth: 12, itemHeight: 6, itemGap: 14
    },
    grid: { left: 42, right: 16, top: 14, bottom: 34 },
    xAxis: {
      type: 'category', data: times, boundaryGap: false,
      axisLine: { lineStyle: { color: 'rgba(100,255,218,0.15)' } },
      axisTick: { show: false },
      axisLabel: { color: '#8892b0', fontSize: 9, rotate: 25 }
    },
    yAxis: {
      type: 'value', minInterval: 1,
      splitLine: { lineStyle: { color: 'rgba(100,255,218,0.05)' } },
      axisLabel: { color: '#8892b0', fontSize: 9 }
    },
    series: [
      {
        name: '正向', type: 'line', data: pos, smooth: true, symbol: 'none',
        lineStyle: { color: '#00ff99', width: 2 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(0,255,153,0.2)' },
            { offset: 1, color: 'rgba(0,255,153,0.0)' }
          ])
        },
        animationDuration: 500, animationEasing: 'cubicInOut'
      },
      {
        name: '中性', type: 'line', data: neu, smooth: true, symbol: 'none',
        lineStyle: { color: '#00cfff', width: 2 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(0,207,255,0.15)' },
            { offset: 1, color: 'rgba(0,207,255,0.0)' }
          ])
        },
        animationDuration: 500, animationEasing: 'cubicInOut'
      },
      {
        name: '负向', type: 'line', data: neg, smooth: true, symbol: 'none',
        lineStyle: { color: '#ff6b6b', width: 2 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(255,107,107,0.2)' },
            { offset: 1, color: 'rgba(255,107,107,0.0)' }
          ])
        },
        animationDuration: 500, animationEasing: 'cubicInOut'
      }
    ]
  }
}

function initChart() {
  const dom = chartDom.value
  if (!dom || dom.clientWidth === 0) { setTimeout(initChart, 200); return }
  chart = echarts.init(dom)
  chart.setOption(buildOption(props.data))
}

watch(() => props.data, (v) => {
  if (chart) chart.setOption(buildOption(v), true)
}, { deep: true })

onMounted(() => {
  nextTick(() => initChart())
  window.addEventListener('resize', () => chart?.resize())
})

onUnmounted(() => {
  window.removeEventListener('resize', () => chart?.resize())
  chart?.dispose()
  chart = null
})
</script>

<style scoped>
.rt-wrap { display: flex; flex-direction: column; height: 100%; }
.rt-head {
  display: flex; align-items: center; gap: 6px;
  padding-bottom: 8px; flex-shrink: 0;
}
.rt-dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: #00cfff;
  box-shadow: 0 0 6px rgba(0,207,255,0.6);
}
.rt-title { font-size: 12px; font-weight: 600; color: #e0e6ff; }
.rt-sub { font-size: 10px; color: #8892b0; margin-left: auto; }
.rt-body { flex: 1; min-height: 140px; width: 100%; }
</style>
