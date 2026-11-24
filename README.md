# 🔒 File Integrity Monitor (FIM) with IoT Integration

A professional file integrity monitoring system with Telegram alerts and ESP32 hardware integration for MSc Digital Forensics & Information Security.

---

## 🚀 Quick Start

### 1. Run the System
**Double-click:** `START.bat`

### 2. Configure What to Monitor
- Press `2` (Change Configuration)
- Add directories or files you want to monitor
- Press `1` (Manage directories) to add folders
- Press `2` (Manage files) to add specific files

### 3. Start Monitoring
- Press `1` (Start Monitoring)
- Your settings are saved automatically!

### 4. Stop Monitoring
- Press `Ctrl+C` to stop

---

## 📋 Features

✅ Real-time file monitoring (create, modify, delete, move)  
✅ SHA-256 hash verification  
✅ Telegram bot alerts with detailed information  
✅ ESP32 hardware alerts (buzzer + LED)  
✅ Comprehensive logging  
✅ Menu-based configuration (settings persist)  
✅ Multi-directory monitoring  
✅ Windows path support  

---

## 🛠️ Installation

### Requirements
- Python 3.7+
- ESP32 board (optional, for hardware alerts)
- Telegram bot (optional, for mobile alerts)

### Quick Install

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd "file integrity iot"
   ```

2. **Install dependencies**
   ```cmd
   pip install -r requirements.txt
   ```

3. **Setup configuration** (Important!)
   ```cmd
   copy config.example.py config.py
   ```
   Then edit `config.py` and add your credentials:
   - Telegram BOT_TOKEN (from @BotFather)
   - Telegram CHAT_ID (run `python get_chat_id.py`)
   - ESP32_IP (from Serial Monitor after upload)

4. **For ESP32**: Update WiFi credentials in `esp32_alert_system.ino`

**📖 Detailed Setup:** See [SETUP.md](SETUP.md) for complete instructions

---

## ⚙️ Configuration

### Using the Menu System (Recommended)
1. Double-click `START.bat`
2. Press `2` for configuration
3. Add/remove directories and files
4. Toggle alerts on/off
5. Settings are saved automatically in `fim_config.json`

### Manual Configuration (Advanced)
Edit `config.py` (create from `config.example.py` if needed):
- `BOT_TOKEN` - Your Telegram bot token
- `CHAT_ID` - Your Telegram chat ID
- `ESP32_IP` - Your ESP32 device IP address
- `TELEGRAM_ENABLED` - Enable/disable Telegram alerts
- `ESP32_ENABLED` - Enable/disable ESP32 hardware alerts

**Note:** `config.py` is gitignored for security. Never commit credentials!

---

## 📱 Telegram Setup

### 1. Create a Bot
1. Open Telegram and search for `@BotFather`
2. Send `/newbot` and follow instructions
3. Copy the bot token (e.g., `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. Get Your Chat ID
1. Search for your bot in Telegram
2. Send `/start` to your bot
3. Run: `python get_chat_id.py`
4. Copy the chat ID shown

### 3. Update Configuration
Edit `config.py`:
```python
BOT_TOKEN = "your-bot-token-here"
CHAT_ID = "your-chat-id-here"
TELEGRAM_ENABLED = True
```

---

## 🔧 ESP32 Hardware Setup

### Components
- ESP32 board
- Buzzer (active/passive)
- LED
- Resistors (220Ω for LED)
- Breadboard and jumper wires

### Connections
- Buzzer: GPIO 25
- LED: GPIO 26
- Power: 5V/3.3V
- Ground: GND

### Upload Code
1. Open `esp32_alert_system/esp32_alert_system.ino` in Arduino IDE
2. Update WiFi credentials:
   ```cpp
   const char* ssid = "Your-WiFi-Name";
   const char* password = "Your-WiFi-Password";
   ```
3. Upload to ESP32
### Update Configuration

Add the ESP32 IP to your `config.py`:

```python
ESP32_IP = "192.168.0.XXX"  # Use the IP from Serial Monitor
```

---

## 📊 What Gets Monitored

The system detects and alerts on:
- ✅ **File Created** - New files added
- ✅ **File Modified** - Content changes detected via SHA-256
- ✅ **File Deleted** - Files removed
- ✅ **File Moved/Renamed** - File path changes

Each alert includes:
- Timestamp
- Event type
- File name and full path
- SHA-256 hashes (before/after for modifications)
- File size (before/after)
- Username
- Computer name

---

## 📁 File Structure

```
file integrity iot/
├── START.bat              # Main launcher (double-click this!)
├── launcher.py            # Menu system
├── fim.py                 # Core monitoring system
├── config.py              # Your credentials (gitignored, create from .example)
├── config.example.py      # Template for config.py
├── fim_config.json        # Saved settings (auto-created, gitignored)
├── get_chat_id.py         # Telegram chat ID helper
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── SETUP.md               # Detailed setup instructions
├── LICENSE                # License information
├── logs/                  # Alert logs (auto-created, gitignored)
│   └── YYYY-MM-DD_fim.log
└── esp32_alert_system/    # ESP32 Arduino code
    └── esp32_alert_system.ino
```

---

## 🎯 Usage Examples

### Example 1: Monitor Your Desktop
```
1. Double-click START.bat
2. Press 2 → 1 → 1
3. Enter: C:\Users\YourName\Desktop
4. Press 4 → 4 → 1
✅ Desktop is now monitored!
```

### Example 2: Monitor Multiple Folders
```
Add multiple directories:
  - C:\Users\YourName\Documents
  - C:\Users\YourName\Desktop
  - D:\Important Files

The system monitors all of them simultaneously.
```

### Example 3: Monitor Specific Files
```
Add important files:
  - C:\Windows\System32\drivers\etc\hosts
  - C:\Users\YourName\.ssh\id_rsa
  - C:\Config\critical_config.ini
```

---

## 📝 Logs

Logs are stored in `logs/YYYY-MM-DD_fim.log` with format:
```
2026-08-08 10:16:14 | File Modified | C:\path\to\file.txt | Old:abc123... | New:def456... | User:username | PC:COMPUTER-NAME
```

View logs from the menu: Press `3` in main menu

---

## 🔍 Troubleshooting

### "No files or directories configured"
→ Press `2` in menu and add at least one file or directory

### ESP32 Not Responding
→ Check ESP32 is powered on and connected to WiFi  
→ Verify IP address in configuration  
→ Test URL: `http://ESP32-IP/status` in browser

### Telegram Alerts Not Working
→ Verify bot token and chat ID are correct  
→ Send `/start` to your bot first  
→ Check `TELEGRAM_ENABLED = True` in config

### "File not found" Warnings
→ Check paths are correct (use full absolute paths)  
→ Verify files/folders actually exist  
→ Ensure proper permissions

---

## 🛡️ Security Notes

- **config.py is gitignored** - Your credentials stay private
- Store bot token securely (never commit to git)
- config.example.py is safe to commit (has no real credentials)
- ESP32 .ino file has placeholder WiFi credentials
- Review logs regularly for unauthorized changes
- Keep ESP32 firmware updated
- Use strong WiFi passwords

**⚠️ Before pushing to git:** Make sure you created config.py from config.example.py and added credentials there (not in fim.py directly)

---

## 📄 License

This project is provided for educational purposes as part of an MSc Digital Forensics & Information Security program.

---

## 🎓 Academic Context

Developed as a practical demonstration of:
- File integrity monitoring concepts
- Real-time security alerting
- IoT integration in cybersecurity
- Digital forensics techniques
- Hash-based change detection

---

## 💡 Tips

- **Settings Persist**: Configure once, use forever
- **Quick Start**: Just press `1` after first setup
- **Multiple Folders**: Monitor as many directories as needed
- **Logs Are Your Friend**: Check logs for detailed history
- **Test First**: Test with a non-critical folder first

---

## 🆘 Quick Commands

| Action | Command |
|--------|---------|
| **Start System** | Double-click `START.bat` |
| **Start Monitoring** | Press `1` in menu |
| **Change Config** | Press `2` in menu |
| **View Logs** | Press `3` in menu |
| **Stop Monitoring** | Press `Ctrl+C` |
| **Get Telegram Chat ID** | `python get_chat_id.py` |

---

**Need Help?** Check `fim.py` for configuration options or review the logs in the `logs/` folder.

---

🎉 **You're all set! Double-click START.bat to begin monitoring!** 🎉
