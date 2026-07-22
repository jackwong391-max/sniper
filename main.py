import os
import time
from threading import Thread
from flask import Flask, jsonify, request
import requests

# ================= 1. Web 伺服器 (包含 Webhook 接收端點) =================
app = Flask('')


@app.route('/')
def home():
  return 'Fast News & Crisis Monitor Active (5s Ultra-Fast)!'


# ⚡ 方案 A：Webhook 接收端點 (接收 Twitter/Truth Social/Zapier 等外部極速推播)
@app.route('/webhook', methods=['POST'])
def receive_webhook():
  try:
    data = request.json or {}
    text = data.get('text', '') or data.get('content', '')
    source = data.get('source', 'Social Media Alert')

    print(f'📥 [Webhook 收到消息] Source: {source}, Text: {text}')

    if text:
      check_and_notify(title=text, source=source, link=data.get('url', ''))
      return jsonify({'status': 'success', 'msg': 'Processed'}), 200
    else:
      return jsonify({'status': 'failed', 'msg': 'No text provided'}), 400
  except Exception as e:
    print(f'❌ Webhook 異常: {e}')
    return jsonify({'error': str(e)}), 400


def run():
  port = int(os.environ.get('PORT', 8080))
  app.run(host='0.0.0.0', port=port)


Thread(target=run).start()

# ================= 2. Telegram & API 設定 =================
TELEGRAM_BOT_TOKEN = '8796696109:AAGTFdMeAEB5_cP70Ka-sqXlm1awVYpbrIA'
TELEGRAM_CHAT_ID = '1423770007'

CHECK_INTERVAL = 5
FMP_API_KEY = os.environ.get('FMP_API_KEY', 'demo')

# ================= 3. 關鍵字庫 =================
CRISIS_KEYWORDS = [
    'Deposit Outflow',
    'Asset-Liability Mismatch',
    'Unrealized Losses',
    'Spike in Borrowing Costs',
    'Uninsured Deposits',
    'Liquidity Crunch',
    'Fire Sale',
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
    'Data-Driven',
    'Policy Divergence',
    'Tightening Plateau',
    'Stagflation',
    'Second-Round Effects',
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
    'Financial Fragmentation',
    'Geopolitical Shock',
    'Friend-shoring',
    'Energy Disruption',
    'oil shock',
    'trade embargo',
    'financial sanctions',
    'strait blockage',
    '石油危機',
    '金融制裁',
    '貿易禁運',
    'tariff',
    'trade war',
    'sanction',
    '關稅',
    '貿易戰',
]

seen_articles = set()


def send_telegram_msg(message):
  url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
  payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message}
  try:
    res = requests.post(url, json=payload, timeout=5)
    if res.status_code != 200:
      print(f'❌ Telegram 發送失敗: {res.text}')
    else:
      print('✅ Telegram 發送成功！')
  except Exception as e:
    print(f'❌ Telegram 發送異常: {e}')


def check_and_notify(title, source, link='', summary=''):
  content = f'{title} {summary}'.lower()

  # 雙向轉小寫比對，確保 100% 抓到
  matched_keywords = [
      kw for kw in CRISIS_KEYWORDS if kw.lower() in content
  ]

  if matched_keywords:
    keywords_str = ', '.join(set(matched_keywords))
    msg = (
        f'⚡【即時市場警報】\n'
        f'📡 來源：{source}\n'
        f'🎯 關鍵字：{keywords_str}\n\n'
        f'📰 內容：{title}\n\n'
        f'🔗 連結：{link if link else "無"}'
    )
    send_telegram_msg(msg)
    print(f'🔥 [已觸發發送] {title}')
  else:
    print(f'⚠️ 收到消息但未匹配到關鍵字: {title}')


# ================= 4. 金融快訊 API 數據源抓取 =================
def fetch_fmp_realtime_news():
  url = f'https://financialmodelingprep.com/api/v3/fmp/articles?page=0&size=5&apikey={FMP_API_KEY}'
  try:
    response = requests.get(url, timeout=3)
    if response.status_code == 200:
      articles = response.json().get('content', [])
      for item in articles:
        article_id = str(item.get('id', item.get('title')))
        if article_id not in seen_articles:
          seen_articles.add(article_id)
          check_and_notify(
              title=item.get('title', ''),
              source='FMP Financial News',
              link=item.get('link', ''),
              summary=item.get('content', ''),
          )
  except Exception as e:
    pass


print('🚀 5 秒極速機器人已啟動...')

# ================= 5. 主輪詢迴圈 =================
while True:
  try:
    fetch_fmp_realtime_news()
  except Exception as e:
    pass

  time.sleep(CHECK_INTERVAL)
