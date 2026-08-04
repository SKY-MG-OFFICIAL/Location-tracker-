# app.py - Simple web server for Render
from flask import Flask
import os
import threading
from telegram_bot import LocationTrackerBot

app = Flask(__name__)

# Start bot in background
def start_bot():
    token = os.environ.get('BOT_TOKEN')
    if token:
        bot = LocationTrackerBot(token)
        bot.run()

thread = threading.Thread(target=start_bot, daemon=True)
thread.start()

@app.route('/')
def home():
    return "✅ Location Tracker Bot is running!"

@app.route('/health')
def health():
    return "OK"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
