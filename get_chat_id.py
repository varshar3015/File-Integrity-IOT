#!/usr/bin/env python3
"""
Get Your Telegram Chat ID
This script will show you the correct chat ID to use
"""

import requests

# Import bot token from config
try:
    from config import BOT_TOKEN
except ImportError:
    print("ERROR: config.py not found!")
    print("Copy config.example.py to config.py and add your BOT_TOKEN")
    exit(1)

print("="*70)
print("GET YOUR TELEGRAM CHAT ID")
print("="*70)
print("\nSTEPS:")
print("1. Open Telegram and find your bot: @pathik_fim_bot")
print("2. Send ANY message to your bot (e.g., 'Hello')")
print("3. Come back here and press Enter")
print()
input("Press Enter after you've sent a message to the bot...")

# Get updates
url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
response = requests.get(url, timeout=5)

if response.status_code == 200:
    data = response.json()
    
    if data.get("ok") and data.get("result"):
        print("\n" + "="*70)
        print("FOUND MESSAGES!")
        print("="*70 + "\n")
        
        for update in data["result"]:
            if "message" in update:
                chat = update["message"]["chat"]
                user = update["message"]["from"]
                message_text = update["message"].get("text", "")
                
                print(f"Message: {message_text}")
                print(f"From: {user.get('first_name', '')} {user.get('last_name', '')}")
                print(f"Username: @{user.get('username', 'N/A')}")
                print(f"\n>>> YOUR CHAT ID: {chat['id']} <<<\n")
                print("="*70)
                print("\nUSE THIS CHAT ID IN YOUR CONFIG!")
                print(f"CHAT_ID = \"{chat['id']}\"")
                print("="*70)
                break
        else:
            print("\n❌ No messages found!")
            print("Make sure you sent a message to @pathik_fim_bot")
    else:
        print("\n❌ No updates found!")
        print("Please send a message to your bot first")
else:
    print(f"\n❌ Error: {response.status_code}")
    print(response.text)
