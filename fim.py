#!/usr/bin/env python3
"""
File Integrity Monitor (FIM) with ESP32 Integration
A production-grade file integrity monitoring system for Windows
Developed for MSc Digital Forensics & Information Security
"""

import os
import sys
import time
import hashlib
import logging
import requests
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, Set, Optional
from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from colorama import init, Fore, Style

# Initialize colorama for Windows console colors
init(autoreset=True)

# ============================================================================
# CONFIGURATION SECTION - Modify these values as needed
# ============================================================================

# Import credentials from config file (gitignored for security)
try:
    from config import BOT_TOKEN, CHAT_ID, ESP32_IP, ESP32_PORT, TELEGRAM_ENABLED, ESP32_ENABLED
except ImportError:
    print(f"{Fore.YELLOW}WARNING: config.py not found!")
    print(f"{Fore.YELLOW}Copy config.example.py to config.py and add your credentials")
    BOT_TOKEN = ""
    CHAT_ID = ""
    ESP32_IP = "192.168.0.100"
    ESP32_PORT = 80
    TELEGRAM_ENABLED = False
    ESP32_ENABLED = False

# Files to monitor (absolute paths)
MONITOR_FILES = [
]

# Directories to monitor (absolute paths, includes subdirectories)
MONITOR_DIRECTORIES = [
    r"C:\Users\pathi\Desktop\FIM_Test",
    r"C:\Users\pathi\Downloads\FIM_Test",
]

# Logging Configuration
LOG_DIR = "logs"
LOG_LEVEL = logging.INFO

# Monitoring Configuration
HASH_ALGORITHM = "sha256"
IGNORE_PATTERNS = [
    "~$*",           # Office temporary files
    "*.tmp",         # Temporary files
    "*.temp",        # Temporary files
    "Thumbs.db",     # Windows thumbnail cache
    "desktop.ini",   # Windows desktop config
    "$RECYCLE.BIN",  # Recycle bin
    "*.lnk",         # Shortcuts
]

# Console Output Configuration
SHOW_VERBOSE = True  # Show detailed monitoring events

# ============================================================================
# FILE HASH MANAGER
# ============================================================================

class FileHashManager:
    """Manages file hashing and integrity verification"""
    
    def __init__(self):
        self.hash_cache: Dict[str, str] = {}
        self.size_cache: Dict[str, int] = {}
        self.lock = threading.Lock()
    
    def calculate_hash(self, file_path: str) -> Optional[str]:
        """Calculate SHA-256 hash of a file"""
        try:
            hash_obj = hashlib.sha256()
            with open(file_path, 'rb') as f:
                # Read file in chunks to handle large files
                for chunk in iter(lambda: f.read(8192), b''):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()
        except (PermissionError, FileNotFoundError, OSError) as e:
            logging.warning(f"Cannot hash {file_path}: {e}")
            return None
    
    def get_file_size(self, file_path: str) -> Optional[int]:
        """Get file size in bytes"""
        try:
            return os.path.getsize(file_path)
        except (FileNotFoundError, OSError):
            return None
    
    def update_hash(self, file_path: str):
        """Update hash for a file and return (old_hash, new_hash, old_size, new_size)"""
        with self.lock:
            old_hash = self.hash_cache.get(file_path)
            old_size = self.size_cache.get(file_path)
            
            new_hash = self.calculate_hash(file_path)
            new_size = self.get_file_size(file_path)
            
            if new_hash:
                self.hash_cache[file_path] = new_hash
            if new_size is not None:
                self.size_cache[file_path] = new_size
            
            return old_hash, new_hash, old_size, new_size
    
    def remove_hash(self, file_path: str):
        """Remove hash entry for deleted file"""
        with self.lock:
            self.hash_cache.pop(file_path, None)
            self.size_cache.pop(file_path, None)
    
    def initialize_file(self, file_path: str):
        """Initialize hash for a new file"""
        if os.path.isfile(file_path):
            file_hash = self.calculate_hash(file_path)
            file_size = self.get_file_size(file_path)
            if file_hash:
                with self.lock:
                    self.hash_cache[file_path] = file_hash
                    if file_size is not None:
                        self.size_cache[file_path] = file_size

# ============================================================================
# ALERT MANAGER
# ============================================================================

class AlertManager:
    """Manages alert notifications via Telegram and ESP32"""
    
    def __init__(self):
        self.telegram_enabled = TELEGRAM_ENABLED and BOT_TOKEN and CHAT_ID
        self.esp32_enabled = ESP32_ENABLED and ESP32_IP
        self.computer_name = os.environ.get('COMPUTERNAME', 'Unknown')
        self.username = os.environ.get('USERNAME', 'Unknown')
    
    def send_telegram_alert(self, message: str, max_retries: int = 3) -> bool:
        """Send alert via Telegram Bot API with retry logic"""
        if not self.telegram_enabled:
            return False
        
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": CHAT_ID,
            "text": message
        }
        
        for attempt in range(max_retries):
            try:
                response = requests.post(url, data=data, timeout=5)
                if response.status_code == 200:
                    return True
                elif response.status_code == 429:  # Rate limited
                    # Extract retry_after from response if available
                    retry_after = response.json().get('parameters', {}).get('retry_after', 2)
                    if attempt < max_retries - 1:
                        logging.warning(f"Telegram rate limited. Retrying in {retry_after}s...")
                        time.sleep(retry_after)
                        continue
                elif response.status_code == 400:  # Bad request
                    try:
                        error_detail = response.json()
                        logging.error(f"Telegram Bad Request: {error_detail}")
                    except:
                        logging.error(f"Telegram Bad Request (400): {response.text}")
                    return False
                else:
                    logging.error(f"Telegram alert failed with status {response.status_code}: {response.text}")
                    return False
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    logging.warning(f"Telegram alert failed: {e}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logging.error(f"Telegram alert failed after {max_retries} attempts: {e}")
                    return False
        
        return False
    
    def trigger_esp32_alert(self) -> bool:
        """Trigger alert on ESP32 device"""
        if not self.esp32_enabled:
            return False
        
        try:
            url = f"http://{ESP32_IP}:{ESP32_PORT}/alert"
            response = requests.get(url, timeout=3)
            return response.status_code == 200
        except Exception as e:
            logging.error(f"ESP32 alert failed: {e}")
            return False
    
    def format_size(self, size_bytes: Optional[int]) -> str:
        """Format file size in human-readable format"""
        if size_bytes is None:
            return "Unknown"
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"
    
    def send_alert(self, event_type: str, file_path: str, 
                   old_hash: Optional[str] = None, new_hash: Optional[str] = None,
                   old_size: Optional[int] = None, new_size: Optional[int] = None):
        """Send comprehensive alert through all channels"""
        
        timestamp = datetime.now().strftime("%d %b %Y %I:%M:%S %p")
        
        # Create console alert
        console_msg = f"\n{Fore.RED}{'='*70}\n"
        console_msg += f"{Fore.RED}[SECURITY ALERT]\n"
        console_msg += f"{Fore.YELLOW}Time:     {timestamp}\n"
        console_msg += f"{Fore.YELLOW}Event:    {event_type}\n"
        console_msg += f"{Fore.YELLOW}File:     {os.path.basename(file_path)}\n"
        console_msg += f"{Fore.YELLOW}Path:     {file_path}\n"
        
        if old_hash:
            console_msg += f"{Fore.CYAN}Old SHA256: {old_hash[:16]}...{old_hash[-16:]}\n"
        if new_hash:
            console_msg += f"{Fore.CYAN}New SHA256: {new_hash[:16]}...{new_hash[-16:]}\n"
        if old_size is not None:
            console_msg += f"{Fore.CYAN}Old Size:   {self.format_size(old_size)}\n"
        if new_size is not None:
            console_msg += f"{Fore.CYAN}New Size:   {self.format_size(new_size)}\n"
        
        console_msg += f"{Fore.MAGENTA}User:     {self.username}\n"
        console_msg += f"{Fore.MAGENTA}Computer: {self.computer_name}\n"
        console_msg += f"{Fore.RED}{'='*70}{Style.RESET_ALL}\n"
        
        print(console_msg)
        
        # Create Telegram alert - use simple format without special Markdown that could break
        telegram_msg = f"🚨 SECURITY ALERT 🚨\n\n"
        telegram_msg += f"Time: {timestamp}\n"
        telegram_msg += f"Event: {event_type}\n"
        telegram_msg += f"File: {os.path.basename(file_path)}\n"
        telegram_msg += f"Path: {file_path}\n\n"
        
        if old_hash:
            telegram_msg += f"Old Hash: {old_hash}\n\n"
        if new_hash:
            telegram_msg += f"New Hash: {new_hash}\n\n"
        if old_size is not None:
            telegram_msg += f"Old Size: {self.format_size(old_size)}\n"
        if new_size is not None:
            telegram_msg += f"New Size: {self.format_size(new_size)}\n\n"
        
        telegram_msg += f"User: {self.username}\n"
        telegram_msg += f"Computer: {self.computer_name}"
        
        # Send alerts
        telegram_sent = False
        esp32_triggered = False
        
        if self.telegram_enabled:
            telegram_sent = self.send_telegram_alert(telegram_msg)
            if telegram_sent:
                print(f"{Fore.GREEN}✓ Telegram alert sent")
            else:
                print(f"{Fore.RED}✗ Telegram alert failed")
        
        if self.esp32_enabled:
            esp32_triggered = self.trigger_esp32_alert()
            if esp32_triggered:
                print(f"{Fore.GREEN}✓ ESP32 alert triggered")
            else:
                print(f"{Fore.RED}✗ ESP32 alert failed")
        
        # Log the event
        log_msg = f"{timestamp} | {event_type} | {file_path} | "
        log_msg += f"Old:{old_hash or 'N/A'} | New:{new_hash or 'N/A'} | "
        log_msg += f"OldSize:{old_size or 'N/A'} | NewSize:{new_size or 'N/A'} | "
        log_msg += f"User:{self.username} | PC:{self.computer_name}"
        logging.info(log_msg)

# ============================================================================
# FILE SYSTEM EVENT HANDLER
# ============================================================================

class IntegrityMonitorHandler(FileSystemEventHandler):
    """Handles file system events and triggers integrity checks"""
    
    def __init__(self, hash_manager: FileHashManager, alert_manager: AlertManager):
        super().__init__()
        self.hash_manager = hash_manager
        self.alert_manager = alert_manager
        self.monitored_paths: Set[str] = set()
        self.processing_lock = threading.Lock()
    
    def should_ignore(self, path: str) -> bool:
        """Check if file should be ignored based on patterns"""
        filename = os.path.basename(path)
        
        for pattern in IGNORE_PATTERNS:
            if pattern.startswith("*"):
                if filename.endswith(pattern[1:]):
                    return True
            elif pattern.endswith("*"):
                if filename.startswith(pattern[:-1]):
                    return True
            elif pattern in path:
                return True
        
        return False
    
    def is_monitored(self, path: str) -> bool:
        """Check if path is in monitored files or directories"""
        path = os.path.abspath(path)
        
        # Check if it's a monitored file
        if path in self.monitored_paths:
            return True
        
        # Check if it's in a monitored directory
        for monitor_dir in MONITOR_DIRECTORIES:
            if path.startswith(os.path.abspath(monitor_dir)):
                return True
        
        return False
    
    def on_created(self, event: FileSystemEvent):
        """Handle file creation events"""
        if event.is_directory or self.should_ignore(event.src_path):
            return
        
        if not self.is_monitored(event.src_path):
            return
        
        with self.processing_lock:
            time.sleep(0.1)  # Brief delay to ensure file is written
            
            if SHOW_VERBOSE:
                print(f"{Fore.CYAN}[CREATED] {event.src_path}")
            
            # Initialize hash for new file
            self.hash_manager.initialize_file(event.src_path)
            
            # Get hash and size
            new_hash = self.hash_manager.hash_cache.get(event.src_path)
            new_size = self.hash_manager.size_cache.get(event.src_path)
            
            # Send alert
            self.alert_manager.send_alert(
                "File Created",
                event.src_path,
                new_hash=new_hash,
                new_size=new_size
            )
    
    def on_deleted(self, event: FileSystemEvent):
        """Handle file deletion events"""
        if event.is_directory or self.should_ignore(event.src_path):
            return
        
        if not self.is_monitored(event.src_path):
            return
        
        with self.processing_lock:
            if SHOW_VERBOSE:
                print(f"{Fore.RED}[DELETED] {event.src_path}")
            
            # Get old hash before removing
            old_hash = self.hash_manager.hash_cache.get(event.src_path)
            old_size = self.hash_manager.size_cache.get(event.src_path)
            
            # Remove from cache
            self.hash_manager.remove_hash(event.src_path)
            
            # Send alert
            self.alert_manager.send_alert(
                "File Deleted",
                event.src_path,
                old_hash=old_hash,
                old_size=old_size
            )
    
    def on_modified(self, event: FileSystemEvent):
        """Handle file modification events"""
        if event.is_directory or self.should_ignore(event.src_path):
            return
        
        if not self.is_monitored(event.src_path):
            return
        
        with self.processing_lock:
            time.sleep(0.1)  # Brief delay to ensure write is complete
            
            if not os.path.isfile(event.src_path):
                return
            
            # Update hash and check for changes
            old_hash, new_hash, old_size, new_size = self.hash_manager.update_hash(event.src_path)
            
            # Only alert if hash actually changed
            if old_hash and new_hash and old_hash != new_hash:
                if SHOW_VERBOSE:
                    print(f"{Fore.YELLOW}[MODIFIED] {event.src_path}")
                
                self.alert_manager.send_alert(
                    "File Modified",
                    event.src_path,
                    old_hash=old_hash,
                    new_hash=new_hash,
                    old_size=old_size,
                    new_size=new_size
                )
            elif not old_hash and new_hash:
                # File was not previously monitored, initialize it
                if SHOW_VERBOSE:
                    print(f"{Fore.CYAN}[DETECTED] {event.src_path}")
    
    def on_moved(self, event: FileSystemEvent):
        """Handle file move/rename events"""
        if event.is_directory or self.should_ignore(event.src_path):
            return
        
        if not (self.is_monitored(event.src_path) or self.is_monitored(event.dest_path)):
            return
        
        with self.processing_lock:
            if SHOW_VERBOSE:
                print(f"{Fore.MAGENTA}[MOVED] {event.src_path} -> {event.dest_path}")
            
            # Get old hash
            old_hash = self.hash_manager.hash_cache.get(event.src_path)
            old_size = self.hash_manager.size_cache.get(event.src_path)
            
            # Update cache with new path
            if old_hash:
                self.hash_manager.remove_hash(event.src_path)
                self.hash_manager.hash_cache[event.dest_path] = old_hash
                if old_size is not None:
                    self.hash_manager.size_cache[event.dest_path] = old_size
            
            # Send alert
            alert_msg = f"File Moved/Renamed\nFrom: {event.src_path}\nTo: {event.dest_path}"
            self.alert_manager.send_alert(
                alert_msg,
                event.dest_path,
                old_hash=old_hash,
                new_hash=old_hash,  # Hash remains same after move
                old_size=old_size,
                new_size=old_size
            )

# ============================================================================
# FILE INTEGRITY MONITOR
# ============================================================================

class FileIntegrityMonitor:
    """Main File Integrity Monitor class"""
    
    def __init__(self):
        self.hash_manager = FileHashManager()
        self.alert_manager = AlertManager()
        self.observer = Observer()
        self.handler = IntegrityMonitorHandler(self.hash_manager, self.alert_manager)
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration"""
        # Create logs directory if it doesn't exist
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)
        
        # Create daily log file
        log_filename = datetime.now().strftime("%Y-%m-%d") + "_fim.log"
        log_path = os.path.join(LOG_DIR, log_filename)
        
        logging.basicConfig(
            level=LOG_LEVEL,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_path),
                logging.StreamHandler()
            ]
        )
        
        # Reduce noise from watchdog and requests
        logging.getLogger('watchdog').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    def initialize_monitoring(self):
        """Initialize file hashes and setup monitoring"""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}File Integrity Monitor (FIM) - Starting...{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*70}\n")
        
        # Initialize monitored files
        print(f"{Fore.GREEN}Initializing monitored files...")
        for file_path in MONITOR_FILES:
            file_path = os.path.abspath(file_path)
            if os.path.isfile(file_path):
                self.hash_manager.initialize_file(file_path)
                self.handler.monitored_paths.add(file_path)
                print(f"{Fore.GREEN}  ✓ {file_path}")
            else:
                print(f"{Fore.YELLOW}  ⚠ File not found: {file_path}")
        
        # Initialize monitored directories
        print(f"\n{Fore.GREEN}Initializing monitored directories...")
        for dir_path in MONITOR_DIRECTORIES:
            dir_path = os.path.abspath(dir_path)
            if os.path.isdir(dir_path):
                print(f"{Fore.GREEN}  ✓ {dir_path}")
                # Initialize all files in directory
                for root, _, files in os.walk(dir_path):
                    for filename in files:
                        file_path = os.path.join(root, filename)
                        if not self.handler.should_ignore(file_path):
                            self.hash_manager.initialize_file(file_path)
            else:
                print(f"{Fore.YELLOW}  ⚠ Directory not found: {dir_path}")
        
        # Setup observers
        print(f"\n{Fore.GREEN}Setting up file system observers...")
        
        # Watch individual files (watch their parent directories)
        watched_dirs = set()
        for file_path in MONITOR_FILES:
            parent_dir = os.path.dirname(os.path.abspath(file_path))
            if os.path.isdir(parent_dir) and parent_dir not in watched_dirs:
                self.observer.schedule(self.handler, parent_dir, recursive=False)
                watched_dirs.add(parent_dir)
        
        # Watch directories recursively
        for dir_path in MONITOR_DIRECTORIES:
            if os.path.isdir(dir_path):
                self.observer.schedule(self.handler, dir_path, recursive=True)
                watched_dirs.add(dir_path)
        
        print(f"{Fore.GREEN}  ✓ Watching {len(watched_dirs)} directories")
        
        # Display configuration status
        print(f"\n{Fore.CYAN}Configuration:")
        print(f"{Fore.CYAN}  Telegram Alerts: {'Enabled' if self.alert_manager.telegram_enabled else 'Disabled'}")
        print(f"{Fore.CYAN}  ESP32 Alerts:    {'Enabled' if self.alert_manager.esp32_enabled else 'Disabled'}")
        print(f"{Fore.CYAN}  Log Directory:   {LOG_DIR}")
        
        print(f"\n{Fore.GREEN}{'='*70}")
        print(f"{Fore.GREEN}MONITORING ACTIVE - Press Ctrl+C to stop{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'='*70}\n")
    
    def test_esp32_connection(self):
        """Test ESP32 connection at startup"""
        if not self.alert_manager.esp32_enabled:
            return
        
        try:
            url = f"http://{ESP32_IP}:{ESP32_PORT}/status"
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                print(f"{Fore.GREEN}  ✓ ESP32 connection verified")
            else:
                print(f"{Fore.YELLOW}  ⚠ ESP32 responded with status {response.status_code}")
        except Exception as e:
            print(f"{Fore.YELLOW}  ⚠ ESP32 connection test failed: {e}")
    
    def start(self):
        """Start the monitoring system"""
        try:
            self.initialize_monitoring()
            self.test_esp32_connection()
            
            self.observer.start()
            
            # Keep running until interrupted
            while True:
                time.sleep(1)
        
        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}{'='*70}")
            print(f"{Fore.YELLOW}Shutting down File Integrity Monitor...{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}{'='*70}\n")
            self.observer.stop()
        
        except Exception as e:
            logging.error(f"Fatal error: {e}")
            print(f"{Fore.RED}Fatal error: {e}")
            self.observer.stop()
        
        finally:
            try:
                self.observer.join()
            except RuntimeError:
                pass  # Observer not started, ignore
            print(f"{Fore.GREEN}File Integrity Monitor stopped gracefully.\n")

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point"""
    # Validate configuration
    if not MONITOR_FILES and not MONITOR_DIRECTORIES:
        print(f"{Fore.RED}ERROR: No files or directories configured for monitoring!")
        print(f"{Fore.YELLOW}Please edit MONITOR_FILES or MONITOR_DIRECTORIES in fim.py")
        sys.exit(1)
    
    # Check for bot token and chat ID if Telegram is enabled
    if TELEGRAM_ENABLED and (not BOT_TOKEN or not CHAT_ID):
        print(f"{Fore.YELLOW}WARNING: Telegram is enabled but BOT_TOKEN or CHAT_ID is missing.")
        print(f"{Fore.YELLOW}Telegram alerts will be disabled. Update configuration to enable.")
    
    # Start monitoring
    fim = FileIntegrityMonitor()
    fim.start()

if __name__ == "__main__":
    main()
