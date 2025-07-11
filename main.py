import time
import os
from dotenv import load_dotenv
from bot.trade_engine import TradeEngine
from binance.client import Client

# Load .env secrets
load_dotenv()

# Get API credentials from environment variables
API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')

# Create Binance API client
client = Client(API_KEY, API_SECRET)

def main():
    engine = TradeEngine(client)
    print("🚀 Starting Crypto Trading Bot...")

    while True:
        print("🔄 Checking market for signals...")
        engine.run()  # Assumes run() checks for signal once
        time.sleep(60)  # Wait 60 seconds before checking again

if __name__ == "__main__":
    main()
