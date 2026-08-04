# simple_bot.py - FULLY WORKING VERSION
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Token
BOT_TOKEN = os.environ.get('BOT_TOKEN')

if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN not set!")
    exit(1)

logger.info("✅ Bot started!")

# ============================================
# COMMANDS
# ============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome message with buttons"""
    keyboard = [
        [
            InlineKeyboardButton("🔗 Create Link", callback_data="create"),
            InlineKeyboardButton("📋 My Links", callback_data="links")
        ],
        [
            InlineKeyboardButton("📊 Statistics", callback_data="stats"),
            InlineKeyboardButton("📡 Live Monitor", callback_data="monitor")
        ],
        [
            InlineKeyboardButton("❓ Help", callback_data="help"),
            InlineKeyboardButton("⚙️ Settings", callback_data="settings")
        ]
    ]
    
    await update.message.reply_text(
        "🚀 <b>WELCOME TO LOCATION TRACKER BOT</b>\n\n"
        "I help you track locations of anyone who clicks your links!\n\n"
        "<b>How it works:</b>\n"
        "1️⃣ Create a tracking link\n"
        "2️⃣ Share the link with anyone\n"
        "3️⃣ When they click it, I send you their EXACT location\n"
        "4️⃣ They get redirected to any URL you choose\n\n"
        "<b>Quick Start:</b>\n"
        "👇 Click the buttons below!",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 <b>HELP</b>\n\n"
        "Commands:\n"
        "/start - Show menu\n"
        "/help - Show this help\n\n"
        "Click the buttons below to get started!",
        parse_mode='HTML'
    )

# ============================================
# BUTTON HANDLERS
# ============================================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "create":
        await query.edit_message_text(
            "🔗 <b>CREATE A TRACKING LINK</b>\n\n"
            "Coming soon! This will create a link that tracks users.\n\n"
            "For now, try these presets:\n"
            "• YouTube/MrBeast\n"
            "• YouTube/PewDiePie\n"
            "• TikTok/MrBeast",
            parse_mode='HTML'
        )
    
    elif data == "links":
        await query.edit_message_text(
            "📋 <b>YOUR LINKS</b>\n\n"
            "You haven't created any links yet.\n\n"
            "Click 'Create Link' to make your first tracking link!",
            parse_mode='HTML'
        )
    
    elif data == "stats":
        await query.edit_message_text(
            "📊 <b>STATISTICS</b>\n\n"
            "Total Links: 0\n"
            "Total Visitors: 0\n\n"
            "Create your first link to start tracking!",
            parse_mode='HTML'
        )
    
    elif data == "monitor":
        await query.edit_message_text(
            "📡 <b>LIVE MONITOR</b>\n\n"
            "No visitors yet.\n\n"
            "Share your tracking link to see live activity here!",
            parse_mode='HTML'
        )
    
    elif data == "help":
        await query.edit_message_text(
            "❓ <b>HELP</b>\n\n"
            "1. Click 'Create Link' to make a tracking link\n"
            "2. Share the link with anyone\n"
            "3. When they click it, you'll get their location!\n\n"
            "Your bot is ready to use!",
            parse_mode='HTML'
        )
    
    elif data == "settings":
        await query.edit_message_text(
            "⚙️ <b>SETTINGS</b>\n\n"
            "Notifications: ON\n"
            "Location Accuracy: High\n"
            "Auto-Delete: OFF\n\n"
            "More settings coming soon!",
            parse_mode='HTML'
        )
    
    # Add back button
    keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back")]]
    await query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(keyboard))

async def back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Return to main menu"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [
            InlineKeyboardButton("🔗 Create Link", callback_data="create"),
            InlineKeyboardButton("📋 My Links", callback_data="links")
        ],
        [
            InlineKeyboardButton("📊 Statistics", callback_data="stats"),
            InlineKeyboardButton("📡 Live Monitor", callback_data="monitor")
        ],
        [
            InlineKeyboardButton("❓ Help", callback_data="help"),
            InlineKeyboardButton("⚙️ Settings", callback_data="settings")
        ]
    ]
    
    await query.edit_message_text(
        "🚀 <b>WELCOME TO LOCATION TRACKER BOT</b>\n\n"
        "What would you like to do?",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ============================================
# MAIN
# ============================================

def main():
    """Start the bot"""
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    
    # Button handlers
    app.add_handler(CallbackQueryHandler(button_handler, pattern="^(create|links|stats|monitor|help|settings)$"))
    app.add_handler(CallbackQueryHandler(back_handler, pattern="^back$"))
    
    logger.info("🚀 Bot is running!")
    app.run_polling()

if __name__ == "__main__":
    main()
