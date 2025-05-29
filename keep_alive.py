# Simple keep-alive mechanism for free tier deployments
import requests
import time
import os
from threading import Thread

def keep_alive():
    """Keep the service alive by pinging itself periodically"""
    app_url = os.getenv('RENDER_EXTERNAL_URL')
    if not app_url:
        return
    
    while True:
        try:
            # Ping every 14 minutes to prevent 15-minute timeout
            time.sleep(14 * 60)
            requests.get(f"{app_url}/")
            print("Keep-alive ping sent")
        except Exception as e:
            print(f"Keep-alive failed: {str(e)}")
            time.sleep(60)

def start_keep_alive():
    """Start keep-alive in background thread"""
    try:
        thread = Thread(target=keep_alive, daemon=True)
        thread.start()
        print("Keep-alive service started")
    except Exception as e:
        print(f"Could not start keep-alive: {str(e)}")