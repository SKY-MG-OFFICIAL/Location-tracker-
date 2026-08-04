# simple_bot.py - TEST VERSION
import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Token
BOT_TOKEN = os.environ.get('BOT_TOKEN')

if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN not set!")
    exit(1)

logger.info("✅ Token found!")

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("✅ Start command received!")
    await update.message.reply_text("✅ YOUR BOT IS WORKING! 🎉")

# Build app
app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))

logger.info("🚀 Bot is running!")
app.run_polling()
