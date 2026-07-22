import os
import time
from threading import Thread
from flask import Flask
import feedparser
import requests

# ================= 1. Web 伺服器 (讓 Render 順利偵測 Port) =================
app = Flask('')


@app.route('/')
def home():
  return 'Market Crisis Monitor Bot is Active!'


def run():
  port = int(os.environ.get('PORT', 8080))
  app.run(host='0.0.0.0', port=port)


# 啟動背景網頁伺服器
Thread(target=run).start()

# ================= 2. Telegram 設定 =================
TELEGRAM_BOT_TOKEN = '8796696109:AAGTFdMeAEB5_cP70Ka-sqXlm1awVYpbrIA'
TELEGRAM_CHAT_ID = '1423770007'

CHECK_INTERVAL = 60  # 每 60 秒檢查一次

# ================= 3. 擴充：重大經濟與金融危機關鍵字 =================
CRISIS_KEYWORDS = [
    # --- 銀行與流動性危機 (Bank & Liquidity Crisis) ---
    'Deposit Outflow'
    'Asset-Liability Mismatch'
    'Unrealized Losses'
    'Spike in Borrowing Costs'
    'Uninsured Deposits'
    'Liquidity Crunch'
    'Fire Sale'
    'bank collapse',
    'bank run',
    'liquidity crisis',
    'credit crunch',
    'insolvency',
    'bankruptcy',
    'default',
    'bailout',
    'counterparty risk',
    '銀行倒閉',
    '擠提',
    '金融危機',
    '破產',
    '債務違約',
    '流動性危機',
    '信貸緊縮',
    # --- 市場暴跌與崩盤 (Market Crash & Extreme Volatility) ---
    'market crash',
    'stock plunge',
    'circuit breaker',
    'panic sell',
    'sell-off',
    'freefall',
    'market meltdown',
    'black swan',
    '崩盤',
    '暴跌',
    '恐慌性拋售',
    '熔斷',
    '黑天鵝',
    # --- 央行與總體經濟巨變 (Central Bank & Macro Disruption) ---
    'Data-Driven'
    'Policy Divergence'
    'Tightening Plateau'
    'Stagflation'
    'Second-Round Effects'
    'emergency rate cut',
    'unplanned fed meeting',
    'rate hike',
    'hyperinflation',
    'stagflation',
    'recession',
    'yield curve inversion',
    '緊急降息',
    '經濟衰退',
    '滯脹',
    '殖利率倒掛',
    # --- 地緣政治與全球衝擊 (Geopolitical & Energy Shock) ---
    'Financial Fragmentation'
    'Geopolitical Shock'
    'Friend-shoring'
    'Energy Disruption'
    'oil shock',
    'trade embargo',
    'financial sanctions',
    'strait blockage',
    '石油危機',
    '金融制裁',
    '貿易禁運',
]

# ================= 4. 擴充：權威財經與市場 RSS 新聞來源 =================
RSS_FEEDS = {
    'Reuters Politics': (
        'https://www.reutersagency.com/feed/?best-topics=political-general&post_type=best'
    ),
    'CNBC Top News': 'https://search.cnbc.com/rs/search/combined/rss/show?id=100003114',
    'CNBC World Economy': (
        'https://search.cnbc.com/rs/search/combined/rss/show?id=20911058'
    ),
    'CNBC Finance': (
        'https://search.cnbc.com/rs/search/combined/rss/show?id=10000664'
    ),
    'MarketWatch Top Stories': (
        'http://feeds.marketwatch.com/marketwatch/topstories/'
    ),
    'MarketWatch Real-time Headlines': (
        'http://feeds.marketwatch.com/marketwatch/bulletins'
    ),
    'FT Global Economy': 'https://www.ft.com/global-economy?format=rss',
}

seen_posts = set()


def send_telegram_msg(message):
  url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
  payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message}
  try:
    requests.post(url, json=payload, timeout=10)
  except Exception as e:
    print(f'發送 Telegram 訊息失敗: {e}')


print('🚨 全球金融危機監控機器人已成功啟動...')

# ================= 5. 核心監控迴圈 =================
while True:
  try:
    for source, feed_url in RSS_FEEDS.items():
      feed = feedparser.parse(feed_url)

      # 每次掃描最新 5 則新聞
      for entry in feed.entries[:5]:
        post_id = entry.get('id', entry.link)

        if post_id not in seen_posts:
          seen_posts.add(post_id)

          title = entry.title
          summary = entry.get('summary', '')
          content_to_check = f'{title} {summary}'.lower()

          # 比對關鍵字
          matched_keywords = [
              kw for kw in CRISIS_KEYWORDS if kw.lower() in content_to_check
          ]

          # 若觸發關鍵字，即時發送警報
          if matched_keywords:
            keywords_str = ', '.join(matched_keywords)
            msg = (
                f'🚨【市場危機警報】\n'
                f'📡 來源：{source}\n'
                f'🎯 觸發關鍵字：{keywords_str}\n\n'
                f'📰 標題：{title}\n\n'
                f'🔗 連結：{entry.link}'
            )
            send_telegram_msg(msg)
            print(f'🔥 攔截到重大新聞: {title} (關鍵字: {keywords_str})')

  except Exception as e:
    print(f'擷取 RSS 時發生錯誤: {e}')

  time.sleep(CHECK_INTERVAL)
