import pandas as pd
import pandas_ta as ta
from binance.client import Client
import datetime

class PatternDetector:
    def __init__(self, client, symbol='BTCUSDT', interval='15m', lookback=100):
        self.client = client
        self.symbol = symbol
        self.interval = interval
        self.lookback = lookback  # number of candles to fetch

    def get_klines(self):
        """
        Fetch candle data from Binance API.
        Returns a pandas DataFrame with OHLCV data.
        """
        klines = self.client.get_klines(symbol=self.symbol, interval=self.interval, limit=self.lookback)
        df = pd.DataFrame(klines, columns=[
            'Open Time', 'Open', 'High', 'Low', 'Close', 'Volume',
            'Close Time', 'Quote Asset Volume', 'Number of Trades',
            'Taker Buy Base Asset Volume', 'Taker Buy Quote Asset Volume', 'Ignore'
        ])
        df['Open'] = df['Open'].astype(float)
        df['High'] = df['High'].astype(float)
        df['Low'] = df['Low'].astype(float)
        df['Close'] = df['Close'].astype(float)
        df['Volume'] = df['Volume'].astype(float)
        df['Open Time'] = pd.to_datetime(df['Open Time'], unit='ms')
        return df

    def calculate_indicators(self, df):
        """
        Calculate EMA20, EMA50, RSI indicators and add to df.
        """
        df['EMA20'] = ta.ema(df['Close'], length=20)
        df['EMA50'] = ta.ema(df['Close'], length=50)
        df['RSI'] = ta.rsi(df['Close'], length=14)
        return df

    def detect_volume_spike(self, df):
        """
        Detect volume spike on the latest candle compared to previous 10 candles average volume.
        """
        avg_vol = df['Volume'].iloc[-11:-1].mean()
        last_vol = df['Volume'].iloc[-1]
        return last_vol > 1.5 * avg_vol  # volume spike if 50% above avg

    def check_confluences(self, df):
        """
        Check if the last candle matches the 3-confluence pattern for LONG trade:
        - Price breaks above recent resistance (here simplified as closing above previous high)
        - EMA20 > EMA50 (bullish)
        - RSI between 55-65
        - Volume spike present
        - Retest of breakout (simplified check)
        Returns True/False
        """
        if len(df) < 60:
            return False

        last = df.iloc[-1]
        prev = df.iloc[-2]

        # EMA crossover bullish
        if df['EMA20'].iloc[-2] < df['EMA50'].iloc[-2]:
            return False
        if df['EMA20'].iloc[-1] <= df['EMA50'].iloc[-1]:
            return False

        # RSI condition
        if not (55 <= last['RSI'] <= 65):
            return False

        # Volume spike
        if not self.detect_volume_spike(df):
            return False

        # Breakout - Close above previous high
        prev_high = df['High'].iloc[-2]
        if last['Close'] <= prev_high:
            return False

        # Retest - simplified: previous candle close near breakout level
        retest_threshold = 0.001  # 0.1%
        if abs(prev['Close'] - prev_high) / prev_high > retest_threshold:
            return False

        return True

    def get_signal(self):
        """
        Fetch data, calculate indicators, and return trade signal
        """
        df = self.get_klines()
        df = self.calculate_indicators(df)
        if self.check_confluences(df):
            return 'long'
        return None


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()  # load API keys from .env file

    API_KEY = os.getenv('BINANCE_API_KEY')
    API_SECRET = os.getenv('BINANCE_API_SECRET')

    client = Client(API_KEY, API_SECRET)

    detector = PatternDetector(client)
    signal = detector.get_signal()
    print(f"Trade signal: {signal}")
