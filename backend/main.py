# ============================================
# 抖音直播弹幕 AI 实时分析平台 — 主程序
# ============================================
# 运行方式：python backend/main.py
# ============================================

import asyncio
import atexit
import os
import queue
import signal
import sys
import threading
import webbrowser

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from collector import run_danmu_monitor

# ========== 全局变量 ==========
danmu_queue: queue.Queue = queue.Queue()
connected_clients: set[WebSocket] = set()
_browser_ref: list = []  # 用于存储 browser 引用

# ========== FastAPI 初始化 ==========
app = FastAPI(
    title="抖音直播弹幕 AI 实时分析平台",
    description="基于 DrissionPage + FastAPI + WebSocket + Vue3 + ECharts",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "status": "运行中",
        "service": "抖音直播弹幕 AI 实时分析平台",
        "websocket": "ws://localhost:8000/ws",
        "connected_clients": len(connected_clients)
    }


# ========== WebSocket ==========
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    print(f"[WebSocket] 新客户端连接，当前连接数: {len(connected_clients)}")

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        print("[WebSocket] 客户端正常断开")
    except Exception as e:
        print(f"[WebSocket] 连接异常: {e}")
    finally:
        connected_clients.discard(websocket)
        print(f"[WebSocket] 客户端断开，当前连接数: {len(connected_clients)}")


# ========== 广播协程 ==========
async def broadcast_danmu():
    """后台协程：持续从队列取弹幕并广播给所有 WebSocket 客户端"""
    print("[广播任务] 弹幕广播协程已启动（每 0.1 秒轮询一次）")

    while True:
        try:
            try:
                danmu_data = danmu_queue.get_nowait()
            except queue.Empty:
                await asyncio.sleep(0.1)
                continue

            disconnected: set[WebSocket] = set()
            for client in connected_clients:
                try:
                    await client.send_json(danmu_data)
                except Exception:
                    disconnected.add(client)

            if disconnected:
                connected_clients.difference_update(disconnected)

        except Exception as e:
            print(f"[广播异常] {e}")
            await asyncio.sleep(1)


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(broadcast_danmu())
    print("[系统] FastAPI 启动完成，后台广播任务已就绪")


# ========== 清理 ==========
def cleanup():
    """退出时清理浏览器进程"""
    try:
        if _browser_ref:
            print("[清理] 正在关闭浏览器...")
            _browser_ref[0].quit()
            _browser_ref.clear()
            print("[清理] 浏览器已关闭")
    except Exception as e:
        print(f"[清理] 关闭浏览器异常: {e}")


# ========== 入口 ==========
if __name__ == '__main__':
    atexit.register(cleanup)
    signal.signal(signal.SIGINT, lambda sig, frame: sys.exit(0))
    signal.signal(signal.SIGTERM, lambda sig, frame: sys.exit(0))

    print("=" * 60)
    print("    🎵  抖音直播弹幕 AI 实时分析平台")
    print("    📡  技术栈: DrissionPage + FastAPI + WebSocket + Vue3 + ECharts")
    print("=" * 60)
    print()
    print("支持链接格式示例：")
    print("  https://live.douyin.com/123456789")
    print()

    live_url = input("请输入抖音直播间地址：").strip()

    if not live_url:
        print("❌ 错误：未输入直播间地址，程序退出。")
        exit(1)

    if "live.douyin.com" not in live_url:
        print("⚠️  警告：输入的地址似乎不是抖音直播间链接，请确认。")
        confirm = input("   是否继续？(y/n): ").strip().lower()
        if confirm != 'y':
            print("程序退出。")
            exit(0)

    print()
    print("-" * 60)
    print("系统启动中...")
    print("-" * 60)

    # 启动弹幕监听线程
    monitor_thread = threading.Thread(
        target=run_danmu_monitor,
        args=(live_url, danmu_queue, _browser_ref),
        daemon=True,
        name="DanmuMonitorThread"
    )
    monitor_thread.start()
    print("[主线程] 弹幕监听线程已启动")

    # 自动打开前端页面
    def open_frontend():
        import time
        time.sleep(2)
        frontend_url = "http://localhost:5173"
        print(f"[自动打开] 正在打开前端页面: {frontend_url}")
        webbrowser.open(frontend_url)

    threading.Thread(target=open_frontend, daemon=True).start()

    print("[主线程] FastAPI 服务器启动中...")
    print()
    print("=" * 60)
    print("  ✅ 服务已启动！")
    print("  📡 WebSocket 地址: ws://localhost:8000/ws")
    print("  🌐 后端 API 地址:  http://localhost:8000")
    print("  🎨 前端运行方式:   cd frontend && npm run dev")
    print("  📖 API 文档地址:   http://localhost:8000/docs")
    print()
    print("  按 Ctrl+C 停止服务器")
    print("=" * 60)

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
