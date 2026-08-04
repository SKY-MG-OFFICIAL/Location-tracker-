# wsgi.py - Web server entry for Render
import os
import sys
from telegram_bot import LocationTrackerBot

def application(environ, start_response):
    """
    Minimal WSGI application for Render.
    This keeps the bot running on Render's web service.
    """
    # Get token from environment
    token = os.environ.get('BOT_TOKEN')
    
    if not token:
        status = '500 Internal Server Error'
        headers = [('Content-Type', 'text/plain')]
        start_response(status, headers)
        return [b'BOT_TOKEN not set!']
    
    # Start the bot in the background
    try:
        # Check if bot is already running
        if not hasattr(application, 'bot_running'):
            print("🚀 Starting Telegram Bot...")
            bot = LocationTrackerBot(token)
            import threading
            thread = threading.Thread(target=bot.run, daemon=True)
            thread.start()
            application.bot_running = True
            print("✅ Bot is running!")
        
        status = '200 OK'
        headers = [('Content-Type', 'text/plain')]
        start_response(status, headers)
        return [b'Bot is running! Check your Telegram.']
        
    except Exception as e:
        status = '500 Internal Server Error'
        headers = [('Content-Type', 'text/plain')]
        start_response(status, headers)
        return [f'Error: {str(e)}'.encode()]
