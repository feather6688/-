# 🎵 抖音直播弹幕智能实时分析平台

[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688)](https://fastapi.tiangolo.com/)
[![Vue 3](https://img.shields.io/badge/Vue-3.5+-4FC08D)](https://vuejs.org/)
[![ECharts](https://img.shields.io/badge/ECharts-5.5+-AA344D)](https://echarts.apache.org/)
[![WebSocket](https://img.shields.io/badge/WebSocket-Real--time-ff69b4)]()
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

> 实时采集抖音直播间弹幕（含表情），WebSocket 毫秒级推送，前端大屏可视化。支持双情绪分析系统、jieba 热词统计、用户活跃排行。

---

## 📖 项目介绍
<img width="2560" height="1330" alt="image" src="https://github.com/user-attachments/assets/e75fb482-660f-4002-8503-51b3e92472e9" />  
本项目是一套基于 Python + FastAPI + Vue3 的抖音直播弹幕实时分析平台。

系统通过 DrissionPage 自动控制浏览器进入直播间，利用 MutationObserver 实时监听页面 DOM 变化，实现直播弹幕毫秒级采集；后端对弹幕数据进行清洗、中文分词、热词统计及情绪分析，并通过 WebSocket 实时推送至前端可视化大屏。  
前端基于 Vue3 + ECharts 构建数据看板，支持弹幕滚动展示、实时情绪监控、热词云分析、用户活跃度排行等功能，实现从数据采集、分析处理到可视化展示的完整闭环。   

该项目完整实现了“数据采集 → 数据处理 → 实时推送 → 数据可视化”的实时数据分析链路，具备一定工程化开发能力与前后端协同能力。 

## ✨ 核心特性
实时采集抖音直播间弹幕  
支持 Emoji 表情解析  
WebSocket 毫秒级数据推送  
jieba 中文分词与热词统计  
实时情绪分析（正向 / 中性 / 负向）  
累计情绪趋势统计  
用户活跃排行榜  
ECharts 数据可视化大屏  
前后端分离架构设计  

## 🎯 适用场景
直播运营数据分析  
舆情监测与弹幕分析  
实时数据可视化学习  
Python 爬虫与数据分析实践  
WebSocket 实时通信项目实践

---

## 🏗️ 技术栈

| 层级 | 技术 | 用途 |
|------|------|------|
| 数据采集 | DrissionPage + Chromium | 操控浏览器访问抖音直播间，注入 JS 监听 DOM |
| 后端框架 | FastAPI | REST API + WebSocket 服务 |
| 服务器 | Uvicorn | ASGI 高性能异步服务器 |
| 中文分词 | jieba | 弹幕内容分词，热词统计 |
| 实时通信 | WebSocket | 全双工长连接，服务端主动推送 |
| 前端框架 | Vue 3 (Composition API) | 响应式数据驱动 UI |
| 构建工具 | Vite | 极速 HMR 开发服务器 |
| 图表库 | ECharts 5 | 面积图 / 环形图 / 折线图 / 柱状图 |

## 🐳 Docker 部署（开发中）

docker-compose up -d
---

## 🔧 系统架构

```
                        数据采集层
     ┌──────────────────────────────────────────┐
     │  抖音直播间                                │
     │  ↓                                        │
     │  DrissionPage 启动 Chromium               │
     │  ↓                                        │
     │  注入 MutationObserver 监听 DOM 变化       │
     │  (含 emoji img alt 提取)                  │
     │  ↓                                        │
     │  console.log('DANMU:...')                 │
     │  ↓                                        │
     │  tab.console.wait() 捕获                  │
     └──────────────────┬───────────────────────┘
                        │
                   数据处理层
     ┌──────────────────┴───────────────────────┐
     │  parse_danmu()  解析用户名 + 弹幕内容      │
     │  ↓                                        │
     │  extract_words()  jieba 分词 + 停用词过滤  │
     │  ↓                                        │
     │  analyze_sentiment()  关键词情绪分类       │
     │  ├─ global_sentiment_stats  累计累加      │
     │  └─ realtime_sentiment_queue  滑动窗口(100) │
     │  ↓                                        │
     │  danmu_queue.put(danmu_data)              │
     └──────────────────┬───────────────────────┘
                        │
                   通信传输层
     ┌──────────────────┴───────────────────────┐
     │  broadcast_danmu() 异步协程               │
     │  ↓                                        │
     │  WebSocket send_json() 广播              │
     │  ws://127.0.0.1:8000/ws                  │
     └──────────────────┬───────────────────────┘
                        │
                   前端展示层
     ┌──────────────────┴───────────────────────┐
     │  Vue 3 App.vue  接收 + 状态管理           │
     │  ├─ DanmuList.vue        实时弹幕列表     │
     │  ├─ RealtimeSentiment.vue  实时情绪环形图 │
     │  ├─ SentimentChart.vue   累计情绪面积图   │
     │  ├─ RealtimeTrendChart.vue 情绪波动折线图 │
     │  ├─ WordCloud.vue        热词圆盘图       │
     │  ├─ TrendChart.vue       弹幕数量趋势     │
     │  └─ UserRank.vue         用户活跃排行     │
     └──────────────────────────────────────────┘
```

---

## 📁 项目结构

```
douyin-danmu-analyzer/
├── backend/                        # Python 后端
│   ├── main.py                     # FastAPI 主入口（WebSocket + 广播）
│   ├── collector.py                # 弹幕采集 + jieba 分词 + 双情绪分析
│   ├── 实时监听（1）.py              # 参考：原始 CSV 输出脚本
│   └── 弹幕实时采集.js               # 参考：原始 MutationObserver 脚本
├── frontend/                       # Vue 3 前端
│   ├── index.html                  # HTML 入口
│   ├── package.json                # 依赖配置
│   ├── vite.config.js              # Vite 配置
│   └── src/
│       ├── main.js                 # Vue 应用启动
│       ├── App.vue                 # 根组件（WebSocket + 状态 + 布局）
│       └── components/
│           ├── DanmuList.vue       # 实时弹幕滚动列表
│           ├── RealtimeSentiment.vue  # 实时情绪环形图（最近100条）
│           ├── SentimentChart.vue     # 累计情绪面积图（整场趋势）
│           ├── RealtimeTrendChart.vue # 实时情绪波动折线图
│           ├── WordCloud.vue       # 热词圆盘图
│           ├── TrendChart.vue      # 弹幕数量趋势图
│           └── UserRank.vue        # 用户活跃排行榜
├── requirements.txt                # Python 依赖
├── .gitignore                      # Git 忽略配置
└── README.md                       # 项目说明
```

---

## 📸 功能展示

### 整体大屏

![大屏概览]
<img width="2560" height="1330" alt="image" src="https://github.com/user-attachments/assets/e75fb482-660f-4002-8503-51b3e92472e9" />


### 实时弹幕列表 + 实时情绪环形图

![弹幕列表]
<img width="410" height="1210" alt="image" src="https://github.com/user-attachments/assets/b4f47060-43d0-4264-8d2d-a4f213a485f5" />
<img width="319" height="295" alt="image" src="https://github.com/user-attachments/assets/1edbcffb-1fda-440d-b49b-4f2df8025a6e" />


### AI 累计情绪趋势 + 计时

![情绪趋势]
<img width="2106" height="508" alt="image" src="https://github.com/user-attachments/assets/f0fca9b8-e985-41ed-897e-4adbd2770185" />


### 热词统计 + 用户排行

![热词排行]
<img width="2105" height="691" alt="image" src="https://github.com/user-attachments/assets/d00bad98-98ca-4587-949f-33ea1d61b6e7" />


> 请将实际截图放入 `screenshots/` 目录并替换上述路径。

---

## ✨ 项目亮点

- **双情绪系统** — 独创"实时情绪（滑动窗口 100 条）+ 累计情绪（整场累加）+ 情绪波动趋势"三层分析，分别回答"此刻""整体""最近变化"
- **WebSocket 实时推送** — 弹幕到达即推送，前端局部更新，不整页刷新
- **emoji 表情支持** — DOM 克隆 + img alt 提取，抖音表情完整抓取
- **页面计时器** — 从第一条弹幕起自动读秒，直观显示直播已进行时长
- **同一浏览器双标签页** — DrissionPage 自动打开直播页 + 分析大屏，不弹多余窗口
- **科技感暗色大屏** — 深色主题 + 霓虹绿配色，赛博朋克风格 UI
- **jieba 中文分词** — 精准热词提取，停用词过滤，自定义直播场景词典
- **模块化组件** — 7 个独立 Vue 组件，ECharts 按需初始化，自动 resize 防内存泄漏

---

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- Chrome 或 Edge 浏览器

### 安装

```bash
# 1. 克隆项目
git clone https://github.com/你的用户名/douyin-danmu-analyzer.git
cd douyin-danmu-analyzer

# 2. 安装 Python 依赖
pip install -r requirements.txt

# 3. 安装前端依赖
cd frontend && npm install && cd ..
```

### 运行

```bash
# 终端 1：启动前端（Vite 开发服务器）
cd frontend
npm run dev

# 终端 2：启动后端（输入直播间地址）
cd backend
python main.py
点击运行 main.py 文件
在下方终端：
粘贴抖音直播间链接，例如：
# https://live.douyin.com/123456789
```

前端访问地址：`http://127.0.0.1:5173`
后端 API 文档：`http://127.0.0.1:8000/docs`

---

## 🔌 WebSocket 接口

**连接地址：** `ws://127.0.0.1:8000/ws`

**消息格式：**

```json
{
  "type": "danmu",
  "name": "小明",
  "content": "主播唱得真好听！[666]",
  "words": ["主播", "好听", "666"],
  "sentiment": "positive",
  "realtime_sentiment": {"positive": 12, "neutral": 5, "negative": 2},
  "global_sentiment": {"positive": 1520, "neutral": 820, "negative": 133},
  "time": "20:15:30"
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `type` | string | 固定 `"danmu"` |
| `name` | string | 发送者用户名 |
| `content` | string | 弹幕文本内容（含表情文字） |
| `words` | array | jieba 分词结果 |
| `sentiment` | string | 本条弹幕情绪：`positive` / `neutral` / `negative` |
| `realtime_sentiment` | object | 最近 100 条弹幕的情绪分布（滑动窗口） |
| `global_sentiment` | object | 从开播到现在的累计情绪分布 |
| `time` | string | 弹幕时间 HH:MM:SS |

---

## 🔮 后续计划

- [ ] NLP 模型情绪分析（替代关键词匹配）
- [ ] 弹幕数据持久化（SQLite / MySQL）
- [ ] 多直播间同时监控
- [ ] Docker 一键部署


---

## 📄 License

MIT License — 仅供学习交流，请遵守抖音平台相关使用规定。

---

## 🙋 FAQ

**Q: 页面打不开 / 127.0.0.1 拒绝连接？**
A: 确认前后端都已启动。Windows 下 `localhost` 可能解析异常，请统一使用 `127.0.0.1`。

**Q: 弹幕没有显示？**
A: 确保输入的直播间正在直播，聊天列表已加载。等待几秒让 MutationObserver 生效。

**Q: WebSocket 显示未连接？**
A: 检查后端是否已启动（访问 `http://127.0.0.1:8000` 确认），然后刷新前端页面。

**Q: 表情/emoji 没抓到？**
A: 重启后端即可，最新代码已包含 img alt 提取逻辑。

**Q: 找不到 Chrome？**
A: DrissionPage 会自动查找系统中的 Chrome 或 Edge，请确保至少安装一个。
