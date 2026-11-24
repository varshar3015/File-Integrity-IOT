"""
Configuration File Template for File Integrity Monitor
Copy this file to 'config.py' and fill in your credentials
"""

# ============================================================================
# TELEGRAM CONFIGURATION
# ============================================================================

# Get your bot token from @BotFather on Telegram
BOT_TOKEN = "your-bot-token-here"

# Get your chat ID by running: python get_chat_id.py
CHAT_ID = "your-chat-id-here"

# ============================================================================
# ESP32 CONFIGURATION
# ============================================================================

# Your ESP32's IP address (get from Serial Monitor after upload)
ESP32_IP = "192.168.0.XXX"
ESP32_PORT = 80

# ============================================================================
# ALERT SETTINGS
# ============================================================================

TELEGRAM_ENABLED = True  # Set to False to disable Telegram alerts
ESP32_ENABLED = True     # Set to False to disable ESP32 alerts
