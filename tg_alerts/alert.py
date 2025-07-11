import os
import asyncio
import logging
from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import RetryAfter, TelegramError
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

logging.basicConfig(
    filename='telegram_alerts.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

bot = Bot(token=TELEGRAM_TOKEN)

async def send_message(text, retries=3, delay=1):
    for attempt in range(retries):
        try:
            await bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=text,
                parse_mode=ParseMode.MARKDOWN_V2
            )
            logging.info(f"Telegram message sent: {text}")
            print(f"Telegram message sent: {text}")
            return
        except RetryAfter as e:
            wait_time = e.retry_after
            logging.warning(f"Rate limited. Waiting {wait_time} seconds.")
            await asyncio.sleep(wait_time)
        except TelegramError as e:
            logging.error(f"Telegram error on attempt {attempt+1}: {e}")
            await asyncio.sleep(delay * (2 ** attempt))
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            await asyncio.sleep(delay * (2 ** attempt))
    logging.error(f"Failed to send Telegram message after {retries} attempts: {text}")

def run_async(coro):
    """Helper to run async coroutine from synchronous code."""
    asyncio.run(coro)

def escape_markdown(text: str) -> str:
    """Escape characters for MarkdownV2 formatting."""
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    return ''.join(f'\\{c}' if c in escape_chars else c for c in text)

async def trade_entry_message(pair, side, risk_pct, reason):
    msg = (
        f"📈 *New Trade Entered*\n"
        f"- Pair: `{escape_markdown(pair)}`\n"
        f"- Side: *{escape_markdown(side.upper())}*\n"
        f"- Risk: *{risk_pct*100:.1f}%*\n"
        f"- Reason: {escape_markdown(reason)}"
    )
    await send_message(msg)

async def trade_exit_message(pair, side, profit_loss):
    msg = (
        f"📉 *Trade Closed*\n"
        f"- Pair: `{escape_markdown(pair)}`\n"
        f"- Side: *{escape_markdown(side.upper())}*\n"
        f"- P/L: *{profit_loss:.2f} USDT*"
    )
    await send_message(msg)

async def error_message(error_text):
    msg = f"⚠️ *Bot Error:* {escape_markdown(error_text)}"
    await send_message(msg)
