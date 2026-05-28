<template>
  <div class="wc-wrap">
    <div class="wc-head">
      <span class="wc-dot">&#9679;</span> 热词圆盘图
    </div>
    <!-- 图表容器：加了 min-height 保证 ECharts 有空间 -->
    <div ref="chartDom" class="wc-body"></div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({ words: { type: Array, required: true } })
const chartDom = ref(null)
let myChart = null

function makeOption(list) {
  const pieData = (list && list.length > 0)
    ? list.map((w, i) => {
        let color = '#4dabf7'
        if (i < 3) color = '#ff6b6b'
        else if (i < 7) color = '#ffa94d'
        return { name: w.name, value: w.value, itemStyle: { color } }
      })
    : []

  return {
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(20,30,60,0.95)',
      borderColor: 'rgba(100,255,218,0.3)',
      textStyle: { color: '#e0e6ff', fontSize: 12 }
    },
    series: [{
      type: 'pie',
      radius: ['35%', '65%'],
      center: ['50%', '50%'],
      roseType: 'area',
      itemStyle: { borderRadius: 4, borderColor: 'rgba(10,14,26,0.8)', borderWidth: 2 },
      label: {
        color: '#8892b0',
        fontSize: 9,
        formatter: '{b}\n{c}次'
      },
      data: pieData
    }]
  }
}

function render() {
  const dom = chartDom.value
  if (!dom) return
  // 确保 ECharts 容器有尺寸
  if (dom.clientHeight === 0) {
    dom.style.height = '200px'
  }
  if (!myChart) {
    myChart = echarts.init(dom)
  }
  myChart.setOption(makeOption(props.words))
}

onMounted(() => {
  nextTick(() => render())
  window.addEventListener('resize', () => myChart?.resize())
})

watch(() => props.words, () => render(), { deep: true })

onUnmounted(() => {
  myChart?.dispose()
  myChart = null
})
</script>

<style scoped>
.wc-wrap { display: flex; flex-direction: column; height: 100%; }
.wc-head {
  font-size: 14px; font-weight: 600; color: #64ffda;
  padding-bottom: 10px; border-bottom: 1px solid rgba(100,255,218,0.15);
  flex-shrink: 0;
}
.wc-dot { font-size: 10px; margin-right: 4px; }
.wc-body { flex: 1; min-height: 180px; width: 100%; }
</style>
