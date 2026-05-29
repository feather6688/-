<!--
SentimentChart.vue — AI 情绪实时分析趋势图（核心主图）
三线平滑渐变面积图：正向 / 中性 / 负向
-->
<template>
  <div class="sc-wrap">
    <div class="sc-head">
      <span class="sc-dot"></span>
      <span class="sc-title">AI 实时情绪分析</span>
      <span class="sc-elapsed">({{ elapsedStr }})</span>
      <span class="sc-badge">LIVE</span>
      <div class="sc-stats">
        <div class="sc-stat pos">
          <span class="sc-stat-val">{{ posPercent }}%</span>
          <span class="sc-stat-label">正向</span>
        </div>
        <div class="sc-stat neu">
          <span class="sc-stat-val">{{ neuPercent }}%</span>
          <span class="sc-stat-label">中性</span>
        </div>
        <div class="sc-stat neg">
          <span class="sc-stat-val">{{ negPercent }}%</span>
          <span class="sc-stat-label">负向</span>
        </div>
      </div>
    </div>
    <div ref="chartDom" class="sc-body"></div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  data: { type: Array, required: true },   // [{time, positive, neutral, negative}, ...]
  elapsed: { type: Number, default: 0 }    // 从第一条弹幕到现在的秒数
})

const chartDom = ref(null)
let chart = null

// 格式化运行时长
const elapsedStr = computed(() => {
  const s = props.elapsed || 0
  const h = Math.floor(s / 3600)
  const m = Math.floor((s % 3600) / 60)
  const sec = s % 60
  if (h > 0) return `${h}时${m}分${sec}秒`
  if (m > 0) return `${m}分${sec}秒`
  return `${sec}秒`
})

// 百分比计算
const posPercent = computed(() => calcPercent('positive'))
const neuPercent = computed(() => calcPercent('neutral'))
const negPercent = computed(() => calcPercent('negative'))

function calcPercent(key) {
  if (!props.data || props.data.length === 0) return 0
  const last = props.data[props.data.length - 1]
  const total = (last.positive || 0) + (last.neutral || 0) + (last.negative || 0)
  if (total === 0) return 0
  return Math.round((last[key] || 0) / total * 100)
}

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
      textStyle: { color: '#e0e6ff', fontSize: 12 },
      axisPointer: { type: 'cross', crossStyle: { color: '#8892b0' } }
    },
    legend: {
      bottom: 0,
      textStyle: { color: '#8892b0', fontSize: 11 },
      data: ['正向情绪', '中性情绪', '负向情绪'],
      itemWidth: 14,
      itemHeight: 8,
      itemGap: 20
    },
    grid: { left: 48, right: 24, top: 20, bottom: 40 },
    xAxis: {
      type: 'category',
      data: times,
      boundaryGap: false,
      axisLine: { lineStyle: { color: 'rgba(100,255,218,0.2)' } },
      axisTick: { show: false },
      axisLabel: { color: '#8892b0', fontSize: 10, rotate: 30 }
    },
    yAxis: {
      type: 'value',
      minInterval: 1,
      splitLine: { lineStyle: { color: 'rgba(100,255,218,0.05)' } },
      axisLabel: { color: '#8892b0', fontSize: 10 }
    },
    series: [
      {
        name: '正向情绪',
        type: 'line',
        data: pos,
        smooth: true,
        symbol: 'none',
        lineStyle: { color: '#00ff99', width: 2, shadowBlur: 8, shadowColor: 'rgba(0,255,153,0.4)' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(0,255,153,0.25)' },
            { offset: 1, color: 'rgba(0,255,153,0.01)' }
          ])
        },
        animationDuration: 600,
        animationEasing: 'cubicInOut'
      },
      {
        name: '中性情绪',
        type: 'line',
        data: neu,
        smooth: true,
        symbol: 'none',
        lineStyle: { color: '#00cfff', width: 2, shadowBlur: 8, shadowColor: 'rgba(0,207,255,0.4)' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(0,207,255,0.20)' },
            { offset: 1, color: 'rgba(0,207,255,0.01)' }
          ])
        },
        animationDuration: 600,
        animationEasing: 'cubicInOut'
      },
      {
        name: '负向情绪',
        type: 'line',
        data: neg,
        smooth: true,
        symbol: 'none',
        lineStyle: { color: '#ff6b6b', width: 2, shadowBlur: 8, shadowColor: 'rgba(255,107,107,0.4)' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(255,107,107,0.25)' },
            { offset: 1, color: 'rgba(255,107,107,0.01)' }
          ])
        },
        animationDuration: 600,
        animationEasing: 'cubicInOut'
      }
    ]
  }
}

function initChart() {
  const dom = chartDom.value
  if (!dom) return
  if (dom.clientWidth === 0 || dom.clientHeight === 0) {
    setTimeout(initChart, 200)
    return
  }
  // 触发浏览器回流，保证容器尺寸
  void dom.offsetHeight
  chart = echarts.init(dom)
  chart.setOption(buildOption(props.data))
}

function onResize() {
  if (chart && chartDom.value) {
    chart.resize()
  }
}

watch(() => props.data, (v) => {
  if (chart) {
    chart.setOption(buildOption(v), true)  // true = notMerge，完整刷新确保动画触发
  }
}, { deep: true })

onMounted(() => {
  nextTick(() => initChart())
  window.addEventListener('resize', onResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', onResize)
  chart?.dispose()
  chart = null
})
</script>

<style scoped>
.sc-wrap {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 260px;
}

/* 标题栏 */
.sc-head {
  display: flex;
  align-items: center;
  gap: 8px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(100,255,218,0.12);
  flex-shrink: 0;
}
.sc-dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  background: #64ffda;
  box-shadow: 0 0 8px rgba(100,255,218,0.6);
  animation: sc-pulse 1.5s infinite;
}
@keyframes sc-pulse {
  0%, 100% { box-shadow: 0 0 4px rgba(100,255,218,0.4); }
  50% { box-shadow: 0 0 12px rgba(100,255,218,0.8); }
}
.sc-title {
  font-size: 14px;
  font-weight: 700;
  color: #64ffda;
  letter-spacing: 1px;
}
.sc-elapsed {
  font-size: 14px;
  color: #8ab4c8;
  font-family: 'Consolas', 'Courier New', monospace;
  font-weight: 600;
}
.sc-badge {
  font-size: 10px;
  font-weight: 700;
  color: #ff6b6b;
  border: 1px solid #ff6b6b;
  padding: 1px 6px;
  border-radius: 3px;
  animation: sc-pulse 2s infinite;
  letter-spacing: 1px;
}

/* 百分比统计 */
.sc-stats {
  margin-left: auto;
  display: flex;
  gap: 16px;
}
.sc-stat {
  display: flex;
  align-items: baseline;
  gap: 3px;
}
.sc-stat-val {
  font-size: 16px;
  font-weight: 700;
  font-family: 'Consolas', 'Courier New', monospace;
}
.sc-stat-label {
  font-size: 10px;
  color: #8892b0;
}
.sc-stat.pos .sc-stat-val { color: #00ff99; }
.sc-stat.neu .sc-stat-val { color: #00cfff; }
.sc-stat.neg .sc-stat-val { color: #ff6b6b; }

/* 图表区 */
.sc-body {
  flex: 1;
  min-height: 200px;
  width: 100%;
}
</style>
