<!--
============================================
App.vue — 根组件
负责：WebSocket连接 + 数据处理 + 大屏布局
============================================
-->
<template>
  <div class="dashboard">
    <!-- 顶部标题栏 -->
    <header class="header">
      <div class="header-left">
        <span class="logo-icon">&#9654;</span>
        <h1 class="title">抖音直播弹幕 AI 实时分析平台</h1>
      </div>
      <div class="header-right">
        <div class="status-badge" :class="{ connected: wsConnected }">
          <span class="status-dot"></span>
          <span>{{ wsConnected ? 'WebSocket 已连接' : 'WebSocket 未连接' }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">弹幕总数</span>
          <span class="stat-value">{{ danmuList.length }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">在线观众</span>
          <span class="stat-value">{{ uniqueUsers }}</span>
        </div>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="main-content">
      <!-- 左侧：弹幕列表 -->
      <section class="panel">
        <DanmuList :list="danmuList" />
      </section>

      <!-- 中间：热词 + 趋势 -->
      <section class="panel-center">
        <div class="chart-row panel">
          <WordCloud :words="topWords" />
        </div>
        <div class="chart-row panel">
          <TrendChart :data="trendData" />
        </div>
      </section>

      <!-- 右侧：用户排行 -->
      <section class="panel">
        <UserRank :users="topUsers" />
      </section>
    </main>

  </div>
</template>

<script setup>
console.log('[App.vue] 组件开始加载...')

import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import DanmuList from './components/DanmuList.vue'
import WordCloud from './components/WordCloud.vue'
import TrendChart from './components/TrendChart.vue'
import UserRank from './components/UserRank.vue'

console.log('[App.vue] 子组件导入完成')

// ============ WebSocket 状态 ============
let ws = null
let reconnectTimer = null
const wsConnected = ref(false)

// ============ 数据状态 ============
const MAX_DANMU = 500
const danmuList = ref([])
const wordCountMap = reactive(new Map())
const trendData = ref([])
const userCountMap = reactive(new Map())

let currentTrendBucket = ''
let currentTrendCount = 0
const MAX_TREND_BUCKETS = 12

// ============ 计算属性 ============
// 在线观众 = 所有发言过的唯一用户数（一直累加）
const uniqueUsers = computed(() => userCountMap.size)

const topWords = computed(() => {
  const arr = []
  for (const [name, value] of wordCountMap) {
    arr.push({ name, value })
  }
  arr.sort((a, b) => b.value - a.value)
  return arr.slice(0, 10)
})

const topUsers = computed(() => {
  const arr = []
  for (const [name, value] of userCountMap) {
    arr.push({ name, value })
  }
  arr.sort((a, b) => b.value - a.value)
  return arr.slice(0, 10)
})

// ============ 趋势桶 ============
function initTrendData() {
  const now = new Date()
  const result = []
  for (let i = MAX_TREND_BUCKETS - 1; i >= 0; i--) {
    const t = new Date(now.getTime() - i * 5000)
    const h = String(t.getHours()).padStart(2, '0')
    const m = String(t.getMinutes()).padStart(2, '0')
    const s = String(t.getSeconds()).padStart(2, '0')
    result.push({ time: h + ':' + m + ':' + s, count: 0 })
  }
  trendData.value = result
  currentTrendBucket = result[result.length - 1].time
  currentTrendCount = 0
}

function getTrendBucket() {
  const now = new Date()
  const sec = Math.floor(now.getSeconds() / 5) * 5
  const h = String(now.getHours()).padStart(2, '0')
  const m = String(now.getMinutes()).padStart(2, '0')
  const s = String(sec).padStart(2, '0')
  return h + ':' + m + ':' + s
}

// ============ 中文分词（简单2-gram） ============
function extractWords(text) {
  // 去掉标点符号
  const cleaned = text.replace(/[，。！？、；：""''（）【】\s\r\n\d]+/g, ' ')
  const words = []
  for (const seg of cleaned.split(' ')) {
    if (seg.length < 2) continue
    for (let i = 0; i < seg.length - 1; i++) {
      words.push(seg.slice(i, i + 2))
    }
  }
  return words
}

// ============ 处理弹幕 ============
function processDanmu(danmu) {
  // 1. 更新列表
  danmuList.value.push(danmu)
  while (danmuList.value.length > MAX_DANMU) {
    danmuList.value.shift()
  }

  // 2. 更新热词
  const words = extractWords(danmu.content)
  for (const w of words) {
    wordCountMap.set(w, (wordCountMap.get(w) || 0) + 1)
  }

  // 3. 更新趋势
  const bucket = getTrendBucket()
  if (bucket !== currentTrendBucket) {
    // 保存当前桶计数
    const arr = trendData.value
    if (arr.length > 0) {
      arr[arr.length - 1].count = currentTrendCount
    }
    // 新桶
    arr.push({ time: bucket, count: 1 })
    while (arr.length > MAX_TREND_BUCKETS) {
      arr.shift()
    }
    currentTrendBucket = bucket
    currentTrendCount = 1
  } else {
    currentTrendCount++
    const arr = trendData.value
    if (arr.length > 0) {
      arr[arr.length - 1].count = currentTrendCount
    }
  }

  // 4. 更新用户累计（用于排行榜，保留所有历史数据）
  userCountMap.set(danmu.name, (userCountMap.get(danmu.name) || 0) + 1)
}

// ============ WebSocket ============
function connectWebSocket() {
  console.log('[WebSocket] 正在连接 ws://localhost:8000/ws ...')
  try {
    ws = new WebSocket('ws://localhost:8000/ws')

    ws.onopen = () => {
      console.log('[WebSocket] 连接成功')
      wsConnected.value = true
      if (reconnectTimer) {
        clearTimeout(reconnectTimer)
        reconnectTimer = null
      }
    }

    ws.onmessage = (event) => {
      try {
        const danmu = JSON.parse(event.data)
        processDanmu(danmu)
      } catch (e) {
        console.error('[WebSocket] 解析失败:', e)
      }
    }

    ws.onclose = () => {
      console.log('[WebSocket] 连接关闭, 3秒后重连')
      wsConnected.value = false
      reconnectTimer = setTimeout(connectWebSocket, 3000)
    }

    ws.onerror = (err) => {
      console.error('[WebSocket] 连接错误 (后端可能未启动)')
    }
  } catch (e) {
    console.error('[WebSocket] 创建失败:', e)
  }
}

function startHeartbeat() {
  setInterval(() => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send('ping')
    }
  }, 30000)
}

// ============ 生命周期 ============
onMounted(() => {
  console.log('[App.vue] 组件已挂载')
  initTrendData()
  connectWebSocket()
  startHeartbeat()
})

onUnmounted(() => {
  if (ws) { ws.close(); ws = null }
  if (reconnectTimer) { clearTimeout(reconnectTimer) }
})

console.log('[App.vue] 组件初始化完成')
</script>

<!-- 全局样式（非 scoped） -->
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  background: #0a0e1a;
  color: #e0e6ff;
  font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
  min-height: 100vh;
  overflow-x: hidden;
}

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: rgba(255,255,255,0.02); }
::-webkit-scrollbar-thumb { background: rgba(100,255,218,0.2); border-radius: 3px; }
</style>

<!-- 组件样式 -->
<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  height: 100vh;
  padding: 16px;
  gap: 16px;
  background-image:
    linear-gradient(rgba(100,255,218,0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(100,255,218,0.03) 1px, transparent 1px);
  background-size: 40px 40px;
}

/* 顶部 */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 24px;
  background: rgba(20,30,60,0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(100,255,218,0.15);
  border-radius: 12px;
  flex-shrink: 0;
}
.header-left { display: flex; align-items: center; gap: 12px; }
.logo-icon { color: #64ffda; font-size: 20px; animation: pulse 2s infinite; }
@keyframes pulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}
.title {
  font-size: 18px;
  font-weight: 700;
  color: #64ffda;
  letter-spacing: 2px;
  font-family: 'Consolas', 'Courier New', monospace;
}
.header-right { display: flex; align-items: center; gap: 24px; }

/* 连接状态 */
.status-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  background: rgba(255,107,107,0.15);
  color: #ff6b6b;
}
.status-badge.connected {
  background: rgba(100,255,218,0.15);
  color: #64ffda;
}
.status-dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  background: currentColor;
  animation: pulse 2s infinite;
}

/* 统计数字 */
.stat-item { display: flex; flex-direction: column; align-items: center; }
.stat-label { font-size: 11px; color: #8892b0; text-transform: uppercase; letter-spacing: 1px; }
.stat-value {
  font-size: 20px;
  font-weight: 700;
  color: #64ffda;
  font-family: 'Consolas', 'Courier New', monospace;
}

/* 主内容区 */
.main-content {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 1.5fr 1fr;
  gap: 16px;
  min-height: 0;
}
.panel-center {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.chart-row {
  flex: 1;
  min-height: 0;
}

/* 面板 */
.panel {
  background: rgba(20,30,60,0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(100,255,218,0.15);
  border-radius: 12px;
  padding: 16px;
  overflow: hidden;
}

</style>
