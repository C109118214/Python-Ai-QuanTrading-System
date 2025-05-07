功能整合需求摘要
功能	說明
✅ 海龜 ADX 策略	計算 ADX 指標，滿足條件則產生買賣訊號
✅ 訊號顯示	在圖上標記 ^（買入）、v（賣出）
✅ 通知功能	使用你提供的 LINE BOT @159pvnwb 立即發送訊號通知
✅ 多市場支援	Crypto（Binance）、ETF/台股（Yahoo Finance）
✅ 幣種查詢 UI	輸入框查詢代碼，下拉選擇 Crypto / ETF / 台股
✅ 查詢區間設定	數字輸入 + 單位選擇（如 30 day、5 hour）
✅ 長期目標	自動化量化交易 + 通知幫手

🧩 介面 UI 初步設計（將會增加以下欄位）
元件	說明
self.asset_type_combo	資產類型：Crypto / ETF / 台股
self.symbol_input	輸入股票/幣種代碼（如 BTCUSDT、0050.TW、VOO）
self.range_input	數字輸入欄，限定 1~60
self.unit_combo	單位選擇欄：sec / min / hour / day / month

🚀 下一步：第一階段整合內容
✅ Step 1. 整合 ADX 海龜策略與訊號標示
在你的 load_data() 裡加上：

計算 ADX。

依據 ADX 門檻產生 position / signal。

在 candlestick 上標示 ^、v。

✅ Step 2. 發 LINE 通知
當偵測到 Signal == 1 或 -1 時，自動觸發：

python
複製
編輯
send_line_notify("🟢 買入訊號出現 (BTCUSDT)")
✅ Step 3. 調整 GUI，加入資產分類 + 時間設定欄位
📩 你現在要做的事
1️⃣ 提供：
✅ LINE Notify 的權杖 token（不是 bot ID，bot ID 是用來加好友的，token 才能發送訊息）

取得方式：LINE Notify

點右上登入 > 我的頁面 > 發行權杖

2️⃣ 決定你要優先整合哪部分：
A. 先完成 GUI + ADX + 訊號標記

B. 再加入 LINE 通知

C. 最後做 Yahoo Finance 資料切換整合

