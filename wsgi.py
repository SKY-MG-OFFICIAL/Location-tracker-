# wsgi.py
import os
import sys
import threading
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import your bot
try:
    from telegram_bot import LocationTrackerBot
    logger.info("✅ Bot class imported successfully!")
except Exception as e:
    logger.error(f"❌ Failed to import bot: {e}")
    sys.exit(1)

# Get token from environment
BOT_TOKEN = os.environ.get('BOT_TOKEN')

if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN not set!")
    sys.exit(1)

logger.info(f"✅ BOT_TOKEN found: {BOT_TOKEN[:10]}...")

# Start the bot
def start_bot():
    try:
        logger.info("🚀 Starting bot...")
        bot = LocationTrackerBot(BOT_TOKEN)
        bot.run()
    except Exception as e:
        logger.error(f"❌ Bot crashed: {e}")

# Run bot in background thread
bot_thread = threading.Thread(target=start_bot, daemon=True)
bot_thread.start()
logger.info("✅ Bot thread started!")

# WSGI application for Render
def application(environ, start_response):
    status = '200 OK'
    headers = [('Content-Type', 'text/plain')]
    start_response(status, headers)
    return [b'Bot is running! Check Telegram.']
