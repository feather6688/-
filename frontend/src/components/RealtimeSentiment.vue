<!--
RealtimeSentiment.vue — 实时情绪环形图（最近100条弹幕）
显示当前直播间气氛：正向 / 中性 / 负向
-->
<template>
  <div class="rs-wrap">
    <div class="rs-head">
      <span class="rs-dot"></span>
      <span class="rs-title">实时直播情绪</span>
      <span class="rs-sub">最近100条弹幕</span>
      <span class="rs-live">LIVE</span>
    </div>
    <div class="rs-body">
      <div ref="chartDom" class="rs-chart"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  data: { type: Object, required: true }  // { positive: N, neutral: N, negative: N }
})

const chartDom = ref(null)
let chart = null

function buildOption(d) {
  const total = d.positive + d.neutral + d.negative || 1
  return {
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(8,12,30,0.95)',
      borderColor: 'rgba(100,255,218,0.25)',
      textStyle: { color: '#e0e6ff', fontSize: 12 },
      formatter: (p) => `${p.name}: ${p.value} 条 (${Math.round(p.value / total * 100)}%)`
    },
    series: [{
      type: 'pie',
      radius: ['42%', '70%'],
      center: ['50%', '52%'],
      avoidLabelOverlap: false,
      emphasis: {
        scaleSize: 6,
        label: { fontSize: 16, fontWeight: 'bold' }
      },
      label: {
        show: true,
        position: 'outside',
        color: '#e0e6ff',
        fontSize: 12,
        fontWeight: 600,
        formatter: '{b} {d}%'
      },
      labelLine: {
        length: 15,
        length2: 10,
        lineStyle: { color: 'rgba(100,255,218,0.5)', width: 1 }
      },
      data: [
        {
          name: '正向',
          value: d.positive,
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 1, 1, [
              { offset: 0, color: '#00ff99' },
              { offset: 1, color: '#00cc77' }
            ]),
            shadowBlur: 10,
            shadowColor: 'rgba(0,255,153,0.4)'
          }
        },
        {
          name: '中性',
          value: d.neutral,
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 1, 1, [
              { offset: 0, color: '#00cfff' },
              { offset: 1, color: '#0099cc' }
            ]),
            shadowBlur: 10,
            shadowColor: 'rgba(0,207,255,0.4)'
          }
        },
        {
          name: '负向',
          value: d.negative,
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 1, 1, [
              { offset: 0, color: '#ff6b6b' },
              { offset: 1, color: '#cc4444' }
            ]),
            shadowBlur: 10,
            shadowColor: 'rgba(255,107,107,0.4)'
          }
        }
      ],
      animationType: 'scale',
      animationEasing: 'elasticOut',
      animationDuration: 800
    }]
  }
}

function initChart() {
  const dom = chartDom.value
  if (!dom || dom.clientWidth === 0) {
    setTimeout(initChart, 200)
    return
  }
  chart = echarts.init(dom)
  chart.setOption(buildOption(props.data))
}

watch(() => props.data, (v) => {
  if (chart) {
    chart.setOption(buildOption(v), true)
  }
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
.rs-wrap {
  display: flex;
  flex-direction: column;
  height: 100%;
}
.rs-head {
  display: flex;
  align-items: center;
  gap: 6px;
  padding-bottom: 8px;
  flex-shrink: 0;
}
.rs-dot {
  width: 7px; height: 7px;
  border-radius: 50%;
  background: #ff6b6b;
  box-shadow: 0 0 8px rgba(255,107,107,0.7);
  animation: rs-blink 1.2s infinite;
}
@keyframes rs-blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}
.rs-title { font-size: 13px; font-weight: 700; color: #e0e6ff; }
.rs-sub { font-size: 10px; color: #8892b0; }
.rs-live {
  margin-left: auto;
  font-size: 9px; font-weight: 700; color: #ff6b6b;
  border: 1px solid #ff6b6b; padding: 1px 5px; border-radius: 3px;
  letter-spacing: 1px;
}
.rs-body { flex: 1; min-height: 0; display: flex; align-items: center; justify-content: center; }
.rs-chart { width: 100%; height: 100%; }
</style>
