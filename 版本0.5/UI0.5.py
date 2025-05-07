# -*- coding: utf-8 -*-
"""
Created on Sat Jan 25 00:25:22 2025

@author: USER
"""

import sys
from PyQt5 import QtWidgets, QtWebEngineWidgets
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QComboBox, QSizePolicy
from binance.client import Client
import pandas as pd
import plotly.graph_objs as go
import talib

# 初始化 Binance API（請輸入您的 API 金鑰）
client = Client(api_key="", api_secret="")

class BinanceApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Binance 仿交易界面")
        self.setGeometry(100, 100, 1200, 800)
        self.initUI()

    def initUI(self):
        # 主布局
        main_layout = QHBoxLayout()

        # 左側圖表區域
        self.chart_view = QtWebEngineWidgets.QWebEngineView()
        self.chart_view.setMinimumWidth(800)

        # 右側功能區域
        right_layout = QVBoxLayout()

        # 輸入與加載區
        self.symbol_input = QLineEdit(self)
        self.symbol_input.setPlaceholderText("查詢幣種（如 BTCUSDT）")
        self.load_button = QPushButton("載入數據", self)
        self.load_button.clicked.connect(self.load_data)

        interval_label = QLabel("選擇時間間隔：", self)
        self.interval_combo = QComboBox(self)
        self.interval_combo.addItems(["1s", "5m", "15m", "30m", "1h", "4h", "1d"])

        right_layout.addWidget(self.symbol_input)
        right_layout.addWidget(interval_label)
        right_layout.addWidget(self.interval_combo)
        right_layout.addWidget(self.load_button)

        # MA 選擇框
        ma_label = QLabel("選擇 MA 週期：", self)
        self.ma_combo = QComboBox(self)
        self.ma_combo.addItems(["MA005", "MA010", "MA020", "MA050", "MA200"])
        self.ma_combo.currentIndexChanged.connect(self.plot_candlestick)

        right_layout.addWidget(ma_label)
        right_layout.addWidget(self.ma_combo)

        # 技術指標按鈕
        indicators = ["副指標", "MACD", "Stoch", "Bollinger Bands", "ADX", "ATR", "CCI", "Stochastic", "SAR"]
        self.indicator_buttons = {}
        for ind in indicators:
            btn = QPushButton(ind, self)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            btn.clicked.connect(lambda _, x=ind: self.plot_sub(x))
            self.indicator_buttons[ind] = btn
            right_layout.addWidget(btn)

        # 訂單簿區域
        self.order_book_table = QTableWidget()
        right_layout.addWidget(QLabel("訂單簿：", self))
        right_layout.addWidget(self.order_book_table)
        # 用 df 的 shape 資訊，讓 tableWidget 繪製相同大小的表格
        
        # 主界面佈局整合
        main_layout.addWidget(self.chart_view)
        main_layout.addLayout(right_layout)

        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def load_data(self):
        #symbol = "BTCUSDT" #測試查詢是否正常運行預設BITUSTD
        symbol = self.symbol_input.text().strip().upper() or "BTCUSDT"  #查詢=輸入結果
        interval = self.interval_combo.currentText()
        try:
            # 根據時間間隔設置查詢的歷史數據範圍
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
        except Exception as e: #如果找不到查詢結果
            QtWidgets.QMessageBox.critical(self, "錯誤", f"無法載入資料，請檢查幣種名稱或網路連線。\n錯誤訊息：{e}")
            print(f"Error loading data: {e}")

    def plot_candlestick(self):
        fig = go.Figure(data=[go.Candlestick(x=self.df.index,
                                             open=self.df['open'],
                                             high=self.df['high'],
                                             low=self.df['low'],
                                             close=self.df['close'])])
        fig.update_layout(
            xaxis=dict(range=[self.df.index[0], self.df.index[-1]])
        )
        # 獲取選擇的 MA 週期
        ma_period = int(self.ma_combo.currentText()[3:])
        ma_column = f"MA{ma_period}"
        if ma_column not in self.df.columns:
            self.df[ma_column] = talib.SMA(self.df['close'], timeperiod=ma_period)
            self.df['EMA'] = talib.EMA(self.df['close'], timeperiod=ma_period)
            self.df['WMA'] = talib.WMA(self.df['close'], timeperiod=ma_period)
            self.df['SAR'] = talib.SAR(self.df['high'], self.df['low'], acceleration=0.02, maximum=0.2)
            
        # 添加 MA 線
        fig.add_trace(go.Scatter(x=self.df.index, y=self.df[ma_column], mode='lines', name=ma_column)) 
        #EMA
        fig.add_trace(go.Scatter(x=self.df.index, y=self.df['EMA'], mode='lines', name='EMA'))
        #WMA
        fig.add_trace(go.Scatter(x=self.df.index, y=self.df['WMA'], mode='lines', name='WMA'))
        #BB
        upper, middle, lower = talib.BBANDS(self.df['close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
        fig.add_trace(go.Scatter(x=self.df.index, y=upper, mode='lines', name='Upper Band'))
        fig.add_trace(go.Scatter(x=self.df.index, y=middle, mode='lines', name='Middle Band'))
        fig.add_trace(go.Scatter(x=self.df.index, y=lower, mode='lines', name='Lower Band'))
        #SAR
        fig.add_trace(go.Scatter(x=self.df.index, y=self.df['SAR'], mode='lines', name='SAR'))
        
        self.chart_view.setHtml(fig.to_html(include_plotlyjs='cdn'))
    def plot_sub(self, indicator):
        fig = go.Figure()
        if indicator == "副指標":
            ##RSI
            self.df['RSI'] = talib.RSI(self.df['close'], timeperiod=14)
            #CCI
            self.df['CCI'] = talib.CCI(self.df['high'], self.df['low'], self.df['close'], timeperiod=20)
            fig.add_trace(go.Scatter(x=self.df.index, y=self.df['RSI'], mode='lines', name='RSI'))
            fig.add_trace(go.Scatter(x=self.df.index, y=self.df['CCI'], mode='lines', name='CCI'))
        self.chart_view.setHtml(fig.to_html(include_plotlyjs='cdn'))
    
        if indicator == "MACD":
            macd, macd_signal, macd_hist = talib.MACD(self.df['close'], fastperiod=12, slowperiod=26, signalperiod=9)
            fig.add_trace(go.Scatter(x=self.df.index, y=macd, mode='lines', name='MACD'))
            fig.add_trace(go.Scatter(x=self.df.index, y=macd_signal, mode='lines', name='Signal'))
            fig.add_trace(go.Bar(x=self.df.index, y=macd_hist, name='Histogram'))
        self.chart_view.setHtml(fig.to_html(include_plotlyjs='cdn'))
            #Stoch
        if indicator == "Stoch":
            self.df['SlowK'], self.df['SlowD'] = talib.STOCH(self.df['high'], self.df['low'], self.df['close'],
                                                         fastk_period=14, slowk_period=3, slowk_matype=0,
                                                         slowd_period=3, slowd_matype=0)
            fig.add_trace(go.Scatter(x=self.df.index, y=self.df['SlowK'], mode='lines', name='SlowK'))
            fig.add_trace(go.Scatter(x=self.df.index, y=self.df['SlowD'], mode='lines', name='SlowD'))
        self.chart_view.setHtml(fig.to_html(include_plotlyjs='cdn'))
    def update_order_book(self):
        cleaned_df = self.df.drop(columns=['ignore'], errors='ignore').dropna()
        self.order_book_table.setColumnCount(len(cleaned_df.columns))
        self.order_book_table.setRowCount(len(cleaned_df))
        self.order_book_table.setHorizontalHeaderLabels(cleaned_df.columns)

        for row_idx, (idx, row) in enumerate(cleaned_df.iterrows()):
            for col_idx, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.order_book_table.setItem(row_idx, col_idx, item)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = BinanceApp()
    window.show()
    sys.exit(app.exec_())