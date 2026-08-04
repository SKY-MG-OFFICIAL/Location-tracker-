import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get token
BOT_TOKEN = os.environ.get('BOT_TOKEN')

if not BOT_TOKEN:
    logger.error("BOT_TOKEN not set!")
    exit(1)

logger.info("Bot started!")

# ============ COMMANDS ============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔗 Create Link", callback_data="create")],
        [InlineKeyboardButton("📋 My Links", callback_data="links")],
        [InlineKeyboardButton("📊 Stats", callback_data="stats")],
        [InlineKeyboardButton("❓ Help", callback_data="help")]
    ]
    
    await update.message.reply_text(
        "🚀 LOCATION TRACKER BOT\n\n"
        "Send me ANY link and I'll create a tracking link!\n\n"
        "Example: https://vt.tiktok.com/xxx",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def create(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔗 SEND ME A LINK\n\n"
        "Send any URL and I'll create a tracking link."
    )

async def links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 YOUR LINKS\n\n"
        "You haven't created any links yet.\n"
        "Send me a link to get started!"
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📊 STATISTICS\n\n"
        "Total Links: 0\n"
        "Total Visitors: 0"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 HELP\n\n"
        "1. Send me ANY link\n"
        "2. I create a tracking link\n"
        "3. Share it with anyone\n"
        "4. Get their location!\n\n"
        "Commands:\n"
        "/start - Menu\n"
        "/create - Create link\n"
        "/links - Your links\n"
        "/stats - Statistics\n"
        "/help - Help"
    )

# ============ BUTTON HANDLERS ============

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "create":
        await query.edit_message_text("🔗 Send me a link!")
    elif data == "links":
        await query.edit_message_text("📋 No links yet. Send me a link!")
    elif data == "stats":
        await query.edit_message_text("📊 Total: 0 links, 0 visitors")
    elif data == "help":
        await query.edit_message_text("📖 Send me a link to get started!")

# ============ MAIN ============

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("create", create))
    app.add_handler(CommandHandler("links", links))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("help", help_command))
    
    # Buttons
    app.add_handler(CallbackQueryHandler(button_handler))
    
    logger.info("Bot is running!")
    app.run_polling()

if __name__ == "__main__":
    main()
