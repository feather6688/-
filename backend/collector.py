# ============================================
# 弹幕采集模块 — DrissionPage 监听抖音直播间
# ============================================

import queue
from datetime import datetime
from DrissionPage import Chromium

# 系统消息关键词（用于过滤）
SYS_KEYWORDS = [
    '来了', '进入直播间', '关注了', '点赞了', '分享了', '送出了',
    '加入粉丝团', '加入团', '成为了', '灯牌', '点亮了',
    '欢迎来到直播间', '严禁未成年人', '理性消费', '谨防网络诈骗',
    '切勿私下交易', '低俗色情', '人身伤害', '诱导消费',
]

# MutationObserver 注入脚本
MONITOR_JS = '''
const targetNode = document.querySelector('[class*="webcast-chatroom___list"]');
if (!targetNode) { console.log('DANMU_SYS:target not found'); }

const config = { childList: true, subtree: true };

const callback = (mutationsList) => {
  for (let mutation of mutationsList){
    if (mutation.type === "childList"){
      mutation.addedNodes.forEach((node)=>{
        if (node.nodeType === 1){
          const text = node.innerText || node.textContent || '';
          if (text.trim().length > 0){
            console.log('DANMU:' + text.trim());
          }
        }
      });
    }
  }
};

const observer = new MutationObserver(callback);
observer.observe(targetNode, config);
'''


def parse_danmu(raw_text: str) -> dict | None:
    """解析弹幕文本，返回 {name, content} 或 None"""
    # 过滤系统消息
    for kw in SYS_KEYWORDS:
        if kw in raw_text:
            return None

    name = ""
    content = ""

    if '：' in raw_text:
        parts = raw_text.split('：', 1)
        name = parts[0].strip().replace('\r', '').replace('\n', '')
        content = parts[1].strip().replace('\r', '').replace('\n', '')
    elif ':' in raw_text:
        parts = raw_text.split(':', 1)
        name = parts[0].strip().replace('\r', '').replace('\n', '')
        content = parts[1].strip().replace('\r', '').replace('\n', '')
    else:
        content = raw_text.strip().replace('\r', '').replace('\n', '')
        # 没冒号且内容超长 → 系统公告
        if len(content) > 40:
            return None

    if not content:
        return None
    if not name:
        name = "用户"

    return {"name": name, "content": content}


def run_danmu_monitor(live_url: str, danmu_queue: queue.Queue, browser_ref: list):
    """
    弹幕监听函数（后台线程入口）

    参数:
        live_url: 抖音直播间地址
        danmu_queue: 线程安全队列，用于向主线程传递弹幕
        browser_ref: 列表，用于存储 browser 引用以便清理
    """
    print(f"[监听线程] 正在启动浏览器并访问直播间...")
    print(f"[监听线程] 目标地址: {live_url}")

    try:
        browser = Chromium()
        browser_ref.append(browser)
        tab = browser.latest_tab
        tab.get(live_url)
        print("[监听线程] 正在加载直播间页面...")

        tab.console.start()
        print("[监听线程] 等待直播间聊天列表加载...")
        tab.wait.eles_loaded('x://*[contains(@class, "webcast-chatroom___list")]')
        print("[监听线程] 直播间聊天列表已加载")

        tab.run_js(MONITOR_JS)
        print("[监听线程] MutationObserver 已注入，开始监听弹幕...")
        print("=" * 50)

        while True:
            msg = tab.console.wait()
            if msg is None:
                continue

            data = msg.text
            if not data.startswith('DANMU:'):
                continue
            data = data[6:]  # 去掉 "DANMU:" 前缀

            parsed = parse_danmu(data)
            if parsed is None:
                continue

            danmu_data = {
                "type": "danmu",
                "name": parsed["name"],
                "content": parsed["content"],
                "time": datetime.now().strftime("%H:%M:%S")
            }

            danmu_queue.put(danmu_data)
            print(f"[弹幕 {danmu_data['time']}] {parsed['name']}: {parsed['content']}")

    except Exception as e:
        print(f"[监听线程] 浏览器启动失败: {e}")
        print("[监听线程] 提示：请确保已安装 Chrome 或 Edge 浏览器")
