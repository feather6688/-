# ============================================
# 弹幕采集模块 — DrissionPage 监听抖音直播间
# ============================================

import queue
from collections import deque
from datetime import datetime
from DrissionPage import Chromium
import jieba

# ========== 双情绪统计系统 ==========
# 累计情绪：从开播起持续累加（用于整场趋势图）
global_sentiment_stats = {"positive": 0, "neutral": 0, "negative": 0}
# 实时情绪：只保留最近 100 条弹幕（滑动窗口，用于环形图）
realtime_sentiment_queue = deque(maxlen=100)


def calc_realtime_sentiment() -> dict:
    """统计最近 100 条弹幕的情绪分布"""
    result = {"positive": 0, "neutral": 0, "negative": 0}
    for label in realtime_sentiment_queue:
        result[label] += 1
    return result

# 直播场景常用词词典
for word in ['牛逼', '牛批', '卧槽', '我靠', '绝了', '无敌', '牛掰', '给力',
             '好听', '好看', '好棒', '好厉害', '太强了', '真牛', '真棒']:
    jieba.add_word(word)

# 停用词：常见虚词不参与热词统计（保留直播高频情绪词如"哈哈""666"）
STOP_WORDS = {
    # 语气助词
    '的', '了', '啊', '呢', '吧', '吗', '嘛', '哦', '嗯', '呀', '哟', '啦', '哪', '哇',
    # 代词
    '我', '你', '他', '她', '它', '们', '这', '那', '哪', '谁', '什么', '怎么', '这个', '那个', '哪个',
    # 常用虚词
    '是', '在', '有', '不', '就', '都', '也', '还', '要', '会', '能', '和', '与', '很', '好',
    '个', '一', '下', '上', '去', '来', '说', '看', '想', '让', '给', '把', '被', '对', '到',
    '没', '真', '太', '可', '多', '大', '小', '人', '可以',
}

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

// 从 DOM 节点提取完整文本（含 emoji 图片的 alt 文本）
function extractFullText(node) {
  const clone = node.cloneNode(true);
  // 将所有 img 标签替换为其 alt 属性值（抖音表情的 alt 就是表情文字）
  const imgs = clone.querySelectorAll('img');
  imgs.forEach(img => {
    const alt = (img.getAttribute('alt') || '').trim();
    if (alt) {
      img.replaceWith(alt);
    }
  });
  return (clone.innerText || clone.textContent || '').trim();
}

const config = { childList: true, subtree: true };

const callback = (mutationsList) => {
  for (let mutation of mutationsList){
    if (mutation.type === "childList"){
      mutation.addedNodes.forEach((node)=>{
        if (node.nodeType === 1){
          const text = extractFullText(node);
          if (text.length > 0){
            console.log('DANMU:' + text);
          }
        }
      });
    }
  }
};

const observer = new MutationObserver(callback);
observer.observe(targetNode, config);
'''


def extract_words(text: str) -> list[str]:
    """使用 jieba 分词，过滤停用词和单字，返回有效词语列表"""
    words = jieba.lcut(text)
    result = []
    for w in words:
        w = w.strip()
        # 过滤：空字符串、单字、停用词、纯标点
        if len(w) < 2:
            continue
        if w in STOP_WORDS:
            continue
        result.append(w)
    return result


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


# ========== 情绪分析 ==========
# 基于关键词匹配的快速情绪分类（轻量级，无需 ML 模型）
POSITIVE_WORDS = {
    '棒', '厉害', '牛', '爱', '喜欢', '赞', '好听', '好看', '支持', '加油',
    '哈哈', '哈哈哈', '绝了', '给力', '无敌', '优秀', '精彩', '完美', '太棒', '牛逼',
    '牛批', '太强', '好厉害', '真牛', '真棒', '开心', '快乐', '笑死', '爱了', '帅',
    '厉害厉害', '顶', '冲', '稳', '到位', '专业', '高质量', '羡慕', '恭喜', '太牛',
    '漂亮', '不错', '666', '888', '太猛', '绝绝子', 'yyds', '好听好听',
    '棒棒', '好棒', '真好', '超棒', '强', '靠谱',
}

NEGATIVE_WORDS = {
    '差', '烂', '垃圾', '恶心', '无语', '吐了', '烦', '讨厌', '不好', '难看', '难听',
    '别播', '下播', '滚', '弱', '菜', '丢人', '什么玩意', '有毒', '别唱', '别跳',
    '唱的啥', '没意思', '无聊', '尴尬', '劣质', '噪音', '吵', '卡', '糊',
    '假唱', '没活', '取关', '太难听', '太难', '别丢人',
}


def analyze_sentiment(text: str) -> str:
    """分析弹幕情绪：positive / negative / neutral"""
    pos = 0
    neg = 0
    for word in POSITIVE_WORDS:
        if word in text:
            pos += 1
    for word in NEGATIVE_WORDS:
        if word in text:
            neg += 1

    if pos > neg:
        return "positive"
    elif neg > pos:
        return "negative"
    else:
        return "neutral"


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

        # 在当前浏览器中新建标签页，打开前端大屏
        browser.new_tab("http://127.0.0.1:5173")
        print("[监听线程] 前端大屏已在新标签页打开")

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

            sentiment_label = analyze_sentiment(parsed["content"])

            # 更新累计情绪（整场直播，持续累加）
            global_sentiment_stats[sentiment_label] += 1
            # 更新实时情绪队列（滑动窗口，只保留最近 100 条）
            realtime_sentiment_queue.append(sentiment_label)

            danmu_data = {
                "type": "danmu",
                "name": parsed["name"],
                "content": parsed["content"],
                "words": extract_words(parsed["content"]),  # jieba 分词
                "sentiment": sentiment_label,               # 本条弹幕情绪
                "realtime_sentiment": calc_realtime_sentiment(),  # 实时情绪分布
                "global_sentiment": dict(global_sentiment_stats), # 累计情绪统计
                "time": datetime.now().strftime("%H:%M:%S")
            }

            danmu_queue.put(danmu_data)
            print(f"[弹幕 {danmu_data['time']}] {parsed['name']}: {parsed['content']} [{sentiment_label}]")

    except Exception as e:
        print(f"[监听线程] 浏览器启动失败: {e}")
        print("[监听线程] 提示：请确保已安装 Chrome 或 Edge 浏览器")
