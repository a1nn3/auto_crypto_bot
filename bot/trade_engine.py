import os
import time
from dotenv import load_dotenv
from binance.client import Client
from strategy.pattern import PatternDetector
from tg_alerts.alert import trade_entry_message, trade_exit_message, error_message


load_dotenv()

API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')

client = Client(API_KEY, API_SECRET)

def run_async(coro):
    import asyncio
    asyncio.run(coro)

class TradeEngine:
    def __init__(self, client, symbol='BTCUSDT', risk_per_trade=0.01):
        self.client = client
        self.symbol = symbol
        self.risk_per_trade = risk_per_trade
        self.detector = PatternDetector(client, symbol=symbol)
        self.open_trades = []

    def get_balance(self):
        balance = self.client.get_asset_balance(asset='USDT')
        return float(balance['free']) if balance else 0

    def calculate_position_size(self, entry_price, stop_loss_price):
        balance = self.get_balance()
        risk_amount = balance * self.risk_per_trade
        risk_per_unit = abs(entry_price - stop_loss_price)
        if risk_per_unit == 0:
            return 0
        qty = risk_amount / risk_per_unit
        return round(qty, 5)

    def execute_trade(self):
        signal = self.detector.get_signal()
        print("🔄 Checking market for signals...")
        if signal == 'long':
            entry_price = float(self.client.get_symbol_ticker(symbol=self.symbol)['price'])
            stop_loss_price = entry_price * 0.995
            take_profit_price = entry_price * 1.01
            qty = self.calculate_position_size(entry_price, stop_loss_price)

            if qty <= 0:
                print("❌ Position size too small, skipping trade.")
                return

            print(f"✅ Placing LONG order for {qty} {self.symbol} at {entry_price}")
            try:
                order = self.client.create_order(
                    symbol=self.symbol,
                    side='BUY',
                    type='MARKET',
                    quantity=qty
                )
                print("📤 Order response:", order)
                run_async(trade_entry_message(
                    self.symbol, 'LONG', self.risk_per_trade, 'Pattern signal matched'
                ))
                trade_info = {
                    'side': 'long',
                    'quantity': qty,
                    'entry_price': entry_price,
                    'stop_loss': stop_loss_price,
                    'take_profit': take_profit_price
                }
                self.open_trades.append(trade_info)
            except Exception as e:
                print(f"❌ Error placing order: {e}")
                run_async(error_message(str(e)))
        else:
            print("❌ No trade signal detected.")

    def monitor_trades(self):
        for trade in self.open_trades[:]:
            try:
                current_price = float(self.client.get_symbol_ticker(symbol=self.symbol)['price'])
                if trade['side'] == 'long':
                    if current_price >= trade['take_profit']:
                        print(f"✅ Take Profit hit at {current_price}")
                        self.close_trade(trade, current_price)
                    elif current_price <= trade['stop_loss']:
                        print(f"🛑 Stop Loss hit at {current_price}")
                        self.close_trade(trade, current_price)
            except Exception as e:
                print(f"❌ Error monitoring trades: {e}")
                run_async(error_message(str(e)))

    def close_trade(self, trade, current_price):
        try:
            order = self.client.create_order(
                symbol=self.symbol,
                side='SELL',
                type='MARKET',
                quantity=trade['quantity']
            )
            print(f"📉 Trade closed: {order}")
            profit_loss = (current_price - trade['entry_price']) * trade['quantity']
            run_async(trade_exit_message(
                self.symbol, trade['side'], profit_loss
            ))
            self.open_trades.remove(trade)
        except Exception as e:
            print(f"❌ Error closing trade: {e}")
            run_async(error_message(str(e)))

    def run(self, check_interval=60):
        while True:
            try:
                self.execute_trade()
                self.monitor_trades()
                time.sleep(check_interval)
            except Exception as e:
                print(f"❌ Error in main loop: {e}")
                run_async(error_message(str(e)))
                time.sleep(check_interval * 2)

if __name__ == '__main__':
    engine = TradeEngine(client)
    engine.run()
