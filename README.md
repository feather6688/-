# 🎵 抖音直播弹幕 AI 实时分析平台

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![Vue](https://img.shields.io/badge/Vue-3.5+-brightgreen.svg)](https://vuejs.org/)
[![ECharts](https://img.shields.io/badge/ECharts-5.5+-orange.svg)](https://echarts.apache.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> 实时采集抖音直播间弹幕，WebSocket 实时推送，前端大屏可视化展示。

---

## 📸 页面展示

> *以下为页面截图预留位置，请替换为实际截图*

```
┌─────────────────────────────────────────────────────┐
│  ▶  抖音直播弹幕 AI 实时分析平台    ● 已连接  总数  观众 │
├────────────┬──────────────────────┬─────────────────┤
│            │                      │                 │
│  实时弹幕   │     热词圆盘图        │  用户活跃排行    │
│  列表      │                      │  Top 10         │
│            │                      │                 │
│  ┌──────┐  │                      │  ┌── 用户A      │
│  │ 用户A │  │     ┌───┐           │  │── 用户B      │
│  │ 666  │  │    /  ●  \          │  │── 用户C      │
│  └──────┘  │    \     /          │  └──────────    │
│  ┌──────┐  │     └───┘           │                 │
│  │ 用户B │  │                      │                 │
│  │ 好棒  │  ├──────────────────────┤                 │
│  └──────┘  │                      │                 │
│            │     弹幕趋势图        │                 │
│   ...      │    ╱╲   ╱╲         │                 │
│            │   ╱  ╲_╱  ╲___     │                 │
│            │                      │                 │
└────────────┴──────────────────────┴─────────────────┘
```

---

## ✨ 功能介绍

| 模块 | 功能 | 说明 |
|------|------|------|
| 🎯 **实时采集** | 抖音弹幕监听 | 基于 DrissionPage + MutationObserver 实时捕获直播间弹幕 |
| 📡 **实时推送** | WebSocket 广播 | 后端通过 WebSocket 将弹幕实时推送给所有前端客户端 |
| 📝 **弹幕列表** | 实时滚动展示 | 最新弹幕自动滚动，保留最近 500 条 |
| 🔥 **热词统计** | 词频圆盘图 | 基于 2-gram 中文分词，统计高频热词 Top 10 |
| 👤 **用户排行** | 活跃用户榜 | 统计发言最多的用户 Top 10 |
| 📈 **趋势图** | 弹幕数量趋势 | 每 5 秒采样，展示近 1 分钟弹幕量变化 |
| 🎨 **暗色大屏** | 科技感 UI | 深色主题 + 霓虹绿配色，适合投屏展示 |

---

## 🏗️ 技术栈

### 后端
- **Python 3.10+** — 主语言
- **FastAPI** — Web 框架，提供 REST API + WebSocket
- **Uvicorn** — ASGI 服务器
- **DrissionPage** — 浏览器自动化，操控 Chrome/Edge 采集弹幕

### 前端
- **Vue 3** — 渐进式前端框架（Composition API）
- **Vite** — 前端构建工具
- **ECharts 5** — 数据可视化图表库

### 通信
- **WebSocket** — 全双工实时通信协议

---

## 📁 项目结构

```
douyin-danmu-analyzer/
├── backend/                     # 后端 Python 代码
│   ├── main.py                  # 主入口：FastAPI + WebSocket + 启动逻辑
│   ├── collector.py             # 弹幕采集：DrissionPage + MutationObserver
│   ├── 实时监听（1）.py           # 参考：原始采集脚本（CSV 输出版）
│   └── 弹幕实时采集.js            # 参考：原始 MutationObserver 脚本
├── frontend/                    # 前端 Vue3 代码
│   ├── index.html               # HTML 入口
│   ├── package.json             # 前端依赖配置
│   ├── vite.config.js           # Vite 配置
│   └── src/
│       ├── main.js              # Vue 应用入口
│       ├── App.vue              # 根组件：WebSocket + 数据处理 + 布局
│       └── components/
│           ├── DanmuList.vue    # 实时弹幕列表组件
│           ├── WordCloud.vue    # 热词圆盘图组件
│           ├── TrendChart.vue   # 趋势折线图组件
│           └── UserRank.vue     # 用户排行榜组件
├── requirements.txt             # Python 依赖
├── .gitignore                   # Git 忽略规则
└── README.md                    # 项目说明（本文件）
```

---

## 🚀 安装教程

### 1. 环境要求

- **Python** 3.10+
- **Node.js** 18+
- **Chrome** 或 **Edge** 浏览器

### 2. 克隆项目

```bash
git clone https://github.com/你的用户名/仓库名.git
cd 仓库名
```

### 3. 安装后端依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 4. 安装前端依赖

```bash
cd frontend
npm install
cd ..
```

---

## 🎮 启动教程

### 第一步：启动前端

打开一个终端：

```bash
cd frontend
npm run dev
```

前端将在 `http://localhost:5173` 启动。

### 第二步：启动后端

打开另一个终端：

```bash
# Windows:
python backend\main.py
# macOS/Linux:
python backend/main.py
```

### 第三步：输入直播间地址

后端启动后会提示输入抖音直播间链接：

```
请输入抖音直播间地址：https://live.douyin.com/123456789
```

### 第四步：查看大屏

浏览器会自动打开 `http://localhost:5173`，即可看到实时弹幕分析大屏。

---

## 🔌 WebSocket 通信流程

```
┌──────────┐     WebSocket      ┌──────────┐     MutationObserver    ┌──────────┐
│  Vue3    │ ◄─────────────────► │  FastAPI │ ◄─────────────────────► │  抖音     │
│  前端    │    ws://8000/ws     │  后端    │    DrissionPage         │  直播间   │
└──────────┘                     └──────────┘                         └──────────┘
     │                                │                                     │
     │  1. 建立 WebSocket 连接         │                                     │
     │ ─────────────────────────────► │                                     │
     │                                │  2. 注入 MutationObserver           │
     │                                │ ──────────────────────────────────► │
     │                                │                                     │
     │                                │  3. 弹幕出现 → console.log()        │
     │                                │ ◄────────────────────────────────── │
     │                                │                                     │
     │  4. 广播弹幕 JSON               │                                     │
     │ ◄───────────────────────────── │                                     │
     │                                │                                     │
     │  5. 更新图表和列表              │                                     │
```

**数据格式示例：**

```json
{
  "type": "danmu",
  "name": "小明",
  "content": "主播唱得真好听！",
  "time": "20:15:30"
}
```

---

## 📖 API 文档

后端启动后，访问以下地址查看自动生成的 API 文档：

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### 接口列表

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 健康检查 + 连接状态 |
| WebSocket | `/ws` | 弹幕实时推送连接 |

---

## 🔮 后续优化方向

- [ ] **情绪分析** — 接入 NLP 模型，分析弹幕情绪倾向（正面/负面/中性）
- [ ] **弹幕关键词告警** — 检测到敏感词时自动提醒
- [ ] **礼物信息采集** — 采集直播间礼物数据
- [ ] **数据持久化** — 弹幕存入 SQLite/MySQL，支持历史回放
- [ ] **多直播间** — 同时监控多个直播间
- [ ] **Docker 部署** — 一键 Docker Compose 启动
- [ ] **移动端适配** — 响应式布局，手机也能查看

---

## 📄 License

MIT License — 仅供学习交流使用，请遵守抖音平台相关规定。

---

## 🙋 常见问题

**Q: 启动后看不到弹幕？**
A: 请确保输入的直播间正在直播，且聊天列表已加载。

**Q: 浏览器没有自动打开？**
A: 手动访问 `http://localhost:5173`。

**Q: WebSocket 显示未连接？**
A: 确认后端已启动（`http://localhost:8000` 可访问），然后刷新前端页面。

**Q: 提示找不到 Chrome？**
A: DrissionPage 会自动查找系统中的 Chrome 或 Edge，请确保已安装其中之一。
