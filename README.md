# auto_crypto_bot


# 🧠 Auto Crypto Bot

A fully automated cryptocurrency trading bot using Binance API, built in Python and Dockerized for deployment.

## ✅ Features
- Real-time pattern detection
- Telegram alerts
- SL/TP logic
- Docker-ready
- 24/7 trading loop

## 🛠 How to Run Locally
```bash
git clone https://github.com/YOUR_USERNAME/auto_crypto_bot.git
cd auto_crypto_bot
docker build -t crypto_bot:latest .
docker run -d --name crypto_bot_container crypto_bot:latest
