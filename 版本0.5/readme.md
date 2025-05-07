## 修正載入查詢只能查詢寫死的BITUSDT
✅ 修正重點（只需 1 行）
🔧 原始程式（錯誤在這裡）：
```python
symbol = "BTCUSDT"
# symbol = self.symbol_input.text()
```
✅ 修改為動態讀取輸入值：
```python
symbol = self.symbol_input.text().strip().upper() or "BTCUSDT"
```
這樣使用者若沒輸入內容，預設使用 BTCUSDT，但只要輸入正確幣種，就能動態查詢。

✅ 建議你也增加一個簡單錯誤提示（使用者輸入錯幣種時）
在 except 區塊中加上 GUI 顯示錯誤的方法，例如用彈窗：

```python
except Exception as e:
    QtWidgets.QMessageBox.critical(self, "錯誤", f"無法載入資料，請檢查幣種名稱或網路連線。\n錯誤訊息：{e}")
    print(f"Error loading data: {e}")
```
✅ 完整的修正範例（load_data 函數）
```python

def load_data(self):
    symbol = self.symbol_input.text().strip().upper() or "BTCUSDT"
    interval = self.interval_combo.currentText()
    try:
        if interval.endswith('m'):
            lookback = "1 day ago UTC"
        elif interval.endswith('h'):
            lookback = "30 days ago UTC"
        elif interval.endswith('s'):
            lookback = "1 min ago UTC"
        else:
            lookback = "90 days ago UTC"

        klines = client.get_historical_klines(symbol, interval, lookback)
        self.df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                                                'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume',
                                                'taker_buy_quote_asset_volume', 'ignore'])
        self.df['timestamp'] = pd.to_datetime(self.df['timestamp'], unit='ms')
        self.df.set_index('timestamp', inplace=True)
        self.df[['open', 'high', 'low', 'close', 'volume']] = self.df[['open', 'high', 'low', 'close', 'volume']].astype(float)

        self.plot_candlestick()
        self.update_order_book()

    except Exception as e:
        QtWidgets.QMessageBox.critical(self, "錯誤", f"無法載入資料，請檢查幣種名稱或網路連線。\n錯誤訊息：{e}")
        print(f"Error loading data: {e}")
```
✅ 測試方式
執行程式。
在「查詢幣種」欄位輸入 ETHUSDT 或 SOLUSDT。
點擊「載入數據」。
觀察圖表是否更新成該幣種的 K 線與指標。

