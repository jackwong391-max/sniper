import time
import requests
import feedparser
import datetime

# ================= 填入你的資料 =================
# 請把雙引號裡面的文字替換成你剛才拿到的 Token 與 ID
TELEGRAM_BOT_TOKEN = "8796696109:AAGTFdWEaEB5_cP70Ka-sqXlWlawVYpbrIA"
TELEGRAM_CHAT_ID = "1423770007"
# ===============================================

# 輪詢間隔時間（60 秒 = 1分鐘檢查一次）
CHECK_INTERVAL = 60 

# 監控的新聞 RSS 來源
RSS_FEEDS = {
    "Reuters Political": "https://www.reutersagency.com/feed/?best-topics=political-general&post_type=best",
    "CNBC Top News": "https://search.cnbc.com/rs/search/combinedradios/rss.xml?partnerId=2000&keywords=breakingnews",
    "FT Global Economy": "https://www.ft.com/global-economy?format=rss"
}

# 觸發警報的關鍵字
CRISIS_KEYWORDS = [
    # 財經危機
    "bank bankruptcy", "bank run", "financial crisis", "market crash", "default", "liquidity crisis",
    "銀行倒閉", "擠兌", "金融危機", "股市暴跌", "違約", "流動性危機", "破產",
    # 地緣政治與軍事衝突
    "war", "missile", "invasion", "sanctions", "state of emergency", "coup", "strait closed",
    "戰爭", "飛彈", "入侵", "制制", "緊急狀態", "政變", "封鎖海峽", "開火"
]

seen_news_ids = set()

def send_telegram(title, link, source, published):
    message = (
        f"🚨 **【重大危機警報】**\n\n"
        f"📌 **新聞標題：** {title}\n"
        f"🌐 **新聞來源：** {source}\n"
        f"⏰ **發布時間：** {published}\n\n"
        f"🔗 [點此閱讀新聞全文]({link})"
    )
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    try:
        res = requests.post(url, json=payload)
        res.raise_for_status()
        print(f"✅ 成功發送警報至 Telegram: {title}")
    except Exception as e:
        print(f"❌ Telegram 發送失敗: {e}")

def check_news():
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] 正在掃描新聞數據源...")
    for source_name, feed_url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                news_id = entry.get("id", entry.link)
                if news_id in seen_news_ids:
                    continue
                
                title = entry.title
                summary = entry.get("summary", "")
                text_to_check = f"{title} {summary}".lower()
                
                if any(kw.lower() in text_to_check for kw in CRISIS_KEYWORDS):
                    published = entry.get("published", "最新突發")
                    send_telegram(title, entry.link, source_name, published)
                
                seen_news_ids.add(news_id)
        except Exception as e:
            print(f"抓取 {source_name} 失敗: {e}")

if __name__ == "__main__":
    print("🤖 危機監控機器人啟動中...")
    # 載入現有新聞標題，避免啟動時被舊新聞洗版
    for feed_url in RSS_FEEDS.values():
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            seen_news_ids.add(entry.get("id", entry.link))
            
    print("✅ 初始新聞載入完成！開始進入 24/7 實時監控模式...")
    
    while True:
        check_news()
        time.sleep(CHECK_INTERVAL)
