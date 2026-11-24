#!/usr/bin/env python3
"""
FIM Launcher - Main Menu Interface
Easy-to-use menu system for File Integrity Monitor
"""

import os
import sys
import json
import subprocess
from colorama import init, Fore, Style

init(autoreset=True)

# Configuration file to store persistent settings
CONFIG_FILE = "fim_config.json"

def clear_screen():
    """Clear the console screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def load_config():
    """Load saved configuration"""
    default_config = {
        "monitor_files": [],
        "monitor_directories": [r"C:\Users\pathi\Desktop\FIM_Test"],
        "telegram_enabled": True,
        "esp32_enabled": True,
        "esp32_ip": "192.168.0.140"
    }
    
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"{Fore.YELLOW}Warning: Could not load config: {e}")
    
    return default_config

def save_config(config):
    """Save configuration to file"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"{Fore.RED}Error saving config: {e}")
        return False

def update_fim_py(config):
    """Update fim.py with current configuration"""
    try:
        with open('fim.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update specific lines more reliably using line-by-line processing
        lines = content.split('\n')
        new_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Handle MONITOR_FILES
            if line.strip().startswith('MONITOR_FILES = ['):
                new_lines.append('MONITOR_FILES = [')
                # Add all files
                for filepath in config['monitor_files']:
                    new_lines.append('    r"' + filepath + '",')
                new_lines.append(']')
                # Skip until closing bracket
                i += 1
                while i < len(lines) and not lines[i].strip() == ']':
                    i += 1
                i += 1
                continue
            
            # Handle MONITOR_DIRECTORIES
            elif line.strip().startswith('MONITOR_DIRECTORIES = ['):
                new_lines.append('MONITOR_DIRECTORIES = [')
                # Add all directories
                for dirpath in config['monitor_directories']:
                    new_lines.append('    r"' + dirpath + '",')
                new_lines.append(']')
                # Skip until closing bracket
                i += 1
                while i < len(lines) and not lines[i].strip() == ']':
                    i += 1
                i += 1
                continue
            
            # Keep the line as-is
            new_lines.append(line)
            i += 1
        
        # Write back to file
        with open('fim.py', 'w', encoding='utf-8', newline='\n') as f:
            f.write('\n'.join(new_lines))
        
        return True
    except Exception as e:
        print(f"{Fore.RED}Error updating fim.py: {e}")
        import traceback
        traceback.print_exc()
        return False

def print_header():
    """Print main menu header"""
    clear_screen()
    print(f"\n{Fore.CYAN}╔══════════════════════════════════════════════════════════════════════╗")
    print(f"{Fore.CYAN}║           FILE INTEGRITY MONITOR - MAIN MENU                         ║")
    print(f"{Fore.CYAN}╚══════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}\n")

def display_current_settings(config):
    """Display current monitoring settings"""
    print(f"{Fore.GREEN}📁 Current Monitoring Configuration:{Style.RESET_ALL}\n")
    
    print(f"{Fore.YELLOW}Files Being Monitored:")
    if config['monitor_files']:
        for i, f in enumerate(config['monitor_files'], 1):
            exists = "✓" if os.path.exists(f) else "✗"
            color = Fore.GREEN if os.path.exists(f) else Fore.RED
            print(f"{color}  {i}. [{exists}] {f}")
    else:
        print(f"{Fore.CYAN}  (No individual files)")
    
    print(f"\n{Fore.YELLOW}Directories Being Monitored:")
    if config['monitor_directories']:
        for i, d in enumerate(config['monitor_directories'], 1):
            exists = "✓" if os.path.exists(d) else "✗"
            color = Fore.GREEN if os.path.exists(d) else Fore.RED
            print(f"{color}  {i}. [{exists}] {d}")
    else:
        print(f"{Fore.CYAN}  (No directories)")
    
    print(f"\n{Fore.YELLOW}Alert Settings:")
    print(f"  Telegram Alerts: {Fore.GREEN if config['telegram_enabled'] else Fore.RED}{'Enabled' if config['telegram_enabled'] else 'Disabled'}")
    print(f"  ESP32 Alerts:    {Fore.GREEN if config['esp32_enabled'] else Fore.RED}{'Enabled' if config['esp32_enabled'] else 'Disabled'}")
    print(f"  ESP32 IP:        {Fore.CYAN}{config['esp32_ip']}")

def start_monitoring(config):
    """Start the FIM with current settings"""
    print_header()
    display_current_settings(config)
    
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.GREEN}Starting File Integrity Monitor...{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*70}\n")
    
    if not config['monitor_files'] and not config['monitor_directories']:
        print(f"{Fore.RED}❌ ERROR: No files or directories configured!")
        print(f"{Fore.YELLOW}Please configure monitoring settings first (Option 2).\n")
        input("Press Enter to return to menu...")
        return
    
    # Update fim.py with current config
    if not update_fim_py(config):
        print(f"{Fore.RED}❌ Failed to update configuration!")
        input("Press Enter to return to menu...")
        return
    
    print(f"{Fore.GREEN}✓ Configuration loaded")
    print(f"{Fore.YELLOW}Press Ctrl+C to stop monitoring and return to menu\n")
    
    try:
        # Run fim.py
        subprocess.run([sys.executable, "fim.py"])
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Monitoring stopped by user")
    except Exception as e:
        print(f"\n{Fore.RED}Error: {e}")
    
    print(f"\n{Fore.CYAN}Returning to main menu...")
    input("Press Enter to continue...")

def manage_directories(config):
    """Manage monitored directories"""
    while True:
        print_header()
        print(f"{Fore.GREEN}📁 Manage Monitored Directories{Style.RESET_ALL}\n")
        
        print(f"{Fore.YELLOW}Current Directories:")
        if config['monitor_directories']:
            for i, d in enumerate(config['monitor_directories'], 1):
                exists = "✓" if os.path.exists(d) else "✗"
                color = Fore.GREEN if os.path.exists(d) else Fore.RED
                print(f"{color}  {i}. [{exists}] {d}")
        else:
            print(f"{Fore.CYAN}  (No directories configured)")
        
        print(f"\n{Fore.CYAN}Options:")
        print(f"{Fore.WHITE}  1. Add a directory")
        print(f"{Fore.WHITE}  2. Remove a directory")
        print(f"{Fore.WHITE}  3. Clear all directories")
        print(f"{Fore.WHITE}  4. Back to main menu")
        
        choice = input(f"\n{Fore.YELLOW}Enter choice (1-4): {Style.RESET_ALL}").strip()
        
        if choice == '1':
            print(f"\n{Fore.YELLOW}Enter directory path to monitor:")
            print(f"{Fore.CYAN}Example: C:\\Users\\pathi\\Desktop\\Important")
            path = input(f"{Fore.WHITE}Path: {Style.RESET_ALL}").strip().strip('"').strip("'")
            
            if path:
                if not os.path.isdir(path):
                    print(f"{Fore.YELLOW}\n⚠ Warning: Directory does not exist!")
                    confirm = input(f"{Fore.YELLOW}Add anyway? (y/n): {Style.RESET_ALL}").lower()
                    if confirm != 'y':
                        continue
                
                if path not in config['monitor_directories']:
                    config['monitor_directories'].append(path)
                    save_config(config)
                    print(f"{Fore.GREEN}✓ Directory added!")
                else:
                    print(f"{Fore.YELLOW}Directory already in list!")
                
                input(f"\n{Fore.CYAN}Press Enter to continue...")
        
        elif choice == '2':
            if not config['monitor_directories']:
                print(f"\n{Fore.YELLOW}No directories to remove!")
                input(f"\n{Fore.CYAN}Press Enter to continue...")
            else:
                try:
                    idx = int(input(f"\n{Fore.YELLOW}Enter number to remove: {Style.RESET_ALL}").strip()) - 1
                    if 0 <= idx < len(config['monitor_directories']):
                        removed = config['monitor_directories'].pop(idx)
                        save_config(config)
                        print(f"{Fore.GREEN}✓ Removed: {removed}")
                    else:
                        print(f"{Fore.RED}Invalid number!")
                except ValueError:
                    print(f"{Fore.RED}Invalid input!")
                
                input(f"\n{Fore.CYAN}Press Enter to continue...")
        
        elif choice == '3':
            confirm = input(f"\n{Fore.RED}Clear ALL directories? (y/n): {Style.RESET_ALL}").lower()
            if confirm == 'y':
                config['monitor_directories'] = []
                save_config(config)
                print(f"{Fore.GREEN}✓ All directories cleared!")
                input(f"\n{Fore.CYAN}Press Enter to continue...")
        
        elif choice == '4':
            break

def manage_files(config):
    """Manage monitored files"""
    while True:
        print_header()
        print(f"{Fore.GREEN}📄 Manage Monitored Files{Style.RESET_ALL}\n")
        
        print(f"{Fore.YELLOW}Current Files:")
        if config['monitor_files']:
            for i, f in enumerate(config['monitor_files'], 1):
                exists = "✓" if os.path.exists(f) else "✗"
                color = Fore.GREEN if os.path.exists(f) else Fore.RED
                print(f"{color}  {i}. [{exists}] {f}")
        else:
            print(f"{Fore.CYAN}  (No files configured)")
        
        print(f"\n{Fore.CYAN}Options:")
        print(f"{Fore.WHITE}  1. Add a file")
        print(f"{Fore.WHITE}  2. Remove a file")
        print(f"{Fore.WHITE}  3. Clear all files")
        print(f"{Fore.WHITE}  4. Back to main menu")
        
        choice = input(f"\n{Fore.YELLOW}Enter choice (1-4): {Style.RESET_ALL}").strip()
        
        if choice == '1':
            print(f"\n{Fore.YELLOW}Enter file path to monitor:")
            print(f"{Fore.CYAN}Example: C:\\Users\\pathi\\Documents\\important.txt")
            path = input(f"{Fore.WHITE}Path: {Style.RESET_ALL}").strip().strip('"').strip("'")
            
            if path:
                if not os.path.isfile(path):
                    print(f"{Fore.YELLOW}\n⚠ Warning: File does not exist!")
                    confirm = input(f"{Fore.YELLOW}Add anyway? (y/n): {Style.RESET_ALL}").lower()
                    if confirm != 'y':
                        continue
                
                if path not in config['monitor_files']:
                    config['monitor_files'].append(path)
                    save_config(config)
                    print(f"{Fore.GREEN}✓ File added!")
                else:
                    print(f"{Fore.YELLOW}File already in list!")
                
                input(f"\n{Fore.CYAN}Press Enter to continue...")
        
        elif choice == '2':
            if not config['monitor_files']:
                print(f"\n{Fore.YELLOW}No files to remove!")
                input(f"\n{Fore.CYAN}Press Enter to continue...")
            else:
                try:
                    idx = int(input(f"\n{Fore.YELLOW}Enter number to remove: {Style.RESET_ALL}").strip()) - 1
                    if 0 <= idx < len(config['monitor_files']):
                        removed = config['monitor_files'].pop(idx)
                        save_config(config)
                        print(f"{Fore.GREEN}✓ Removed: {removed}")
                    else:
                        print(f"{Fore.RED}Invalid number!")
                except ValueError:
                    print(f"{Fore.RED}Invalid input!")
                
                input(f"\n{Fore.CYAN}Press Enter to continue...")
        
        elif choice == '3':
            confirm = input(f"\n{Fore.RED}Clear ALL files? (y/n): {Style.RESET_ALL}").lower()
            if confirm == 'y':
                config['monitor_files'] = []
                save_config(config)
                print(f"{Fore.GREEN}✓ All files cleared!")
                input(f"\n{Fore.CYAN}Press Enter to continue...")
        
        elif choice == '4':
            break

def manage_settings(config):
    """Manage alert settings"""
    while True:
        print_header()
        print(f"{Fore.GREEN}⚙️ Alert Settings{Style.RESET_ALL}\n")
        
        print(f"{Fore.YELLOW}Current Settings:")
        print(f"  1. Telegram Alerts: {Fore.GREEN if config['telegram_enabled'] else Fore.RED}{'Enabled' if config['telegram_enabled'] else 'Disabled'}")
        print(f"  2. ESP32 Alerts:    {Fore.GREEN if config['esp32_enabled'] else Fore.RED}{'Enabled' if config['esp32_enabled'] else 'Disabled'}")
        print(f"  3. ESP32 IP:        {Fore.CYAN}{config['esp32_ip']}")
        
        print(f"\n{Fore.CYAN}Options:")
        print(f"{Fore.WHITE}  1. Toggle Telegram alerts")
        print(f"{Fore.WHITE}  2. Toggle ESP32 alerts")
        print(f"{Fore.WHITE}  3. Change ESP32 IP address")
        print(f"{Fore.WHITE}  4. Back to main menu")
        
        choice = input(f"\n{Fore.YELLOW}Enter choice (1-4): {Style.RESET_ALL}").strip()
        
        if choice == '1':
            config['telegram_enabled'] = not config['telegram_enabled']
            save_config(config)
            status = "enabled" if config['telegram_enabled'] else "disabled"
            print(f"{Fore.GREEN}✓ Telegram alerts {status}!")
            input(f"\n{Fore.CYAN}Press Enter to continue...")
        
        elif choice == '2':
            config['esp32_enabled'] = not config['esp32_enabled']
            save_config(config)
            status = "enabled" if config['esp32_enabled'] else "disabled"
            print(f"{Fore.GREEN}✓ ESP32 alerts {status}!")
            input(f"\n{Fore.CYAN}Press Enter to continue...")
        
        elif choice == '3':
            print(f"\n{Fore.YELLOW}Current IP: {config['esp32_ip']}")
            new_ip = input(f"{Fore.WHITE}Enter new IP address: {Style.RESET_ALL}").strip()
            if new_ip:
                config['esp32_ip'] = new_ip
                save_config(config)
                print(f"{Fore.GREEN}✓ ESP32 IP updated!")
            input(f"\n{Fore.CYAN}Press Enter to continue...")
        
        elif choice == '4':
            break

def configure_monitoring(config):
    """Configuration submenu"""
    while True:
        print_header()
        display_current_settings(config)
        
        print(f"\n{Fore.CYAN}Configuration Options:")
        print(f"{Fore.WHITE}  1. Manage directories")
        print(f"{Fore.WHITE}  2. Manage files")
        print(f"{Fore.WHITE}  3. Alert settings")
        print(f"{Fore.WHITE}  4. Back to main menu")
        
        choice = input(f"\n{Fore.YELLOW}Enter choice (1-4): {Style.RESET_ALL}").strip()
        
        if choice == '1':
            manage_directories(config)
        elif choice == '2':
            manage_files(config)
        elif choice == '3':
            manage_settings(config)
        elif choice == '4':
            break

def main_menu():
    """Main menu loop"""
    config = load_config()
    
    while True:
        print_header()
        display_current_settings(config)
        
        print(f"\n{Fore.CYAN}╔══════════════════════════════════════════════════════════════════════╗")
        print(f"{Fore.CYAN}║  MAIN MENU                                                           ║")
        print(f"{Fore.CYAN}╚══════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}\n")
        
        print(f"{Fore.WHITE}  1. ▶️  Start Monitoring (with above settings)")
        print(f"{Fore.WHITE}  2. ⚙️  Change Configuration")
        print(f"{Fore.WHITE}  3. 📊 View Logs")
        print(f"{Fore.WHITE}  4. ❌ Exit")
        
        choice = input(f"\n{Fore.YELLOW}Enter your choice (1-4): {Style.RESET_ALL}").strip()
        
        if choice == '1':
            start_monitoring(config)
        
        elif choice == '2':
            configure_monitoring(config)
            config = load_config()  # Reload config after changes
        
        elif choice == '3':
            print_header()
            print(f"{Fore.GREEN}📊 Recent Logs:{Style.RESET_ALL}\n")
            
            log_dir = "logs"
            if os.path.exists(log_dir):
                log_files = sorted([f for f in os.listdir(log_dir) if f.endswith('.log')], reverse=True)
                if log_files:
                    print(f"{Fore.YELLOW}Available log files:")
                    for i, log in enumerate(log_files[:5], 1):
                        print(f"{Fore.CYAN}  {i}. {log}")
                    
                    print(f"\n{Fore.WHITE}Open logs folder? (y/n): ", end='')
                    if input().lower() == 'y':
                        os.startfile(os.path.abspath(log_dir))
                else:
                    print(f"{Fore.YELLOW}No log files found yet.")
            else:
                print(f"{Fore.YELLOW}Logs directory not found. It will be created when monitoring starts.")
            
            input(f"\n{Fore.CYAN}Press Enter to continue...")
        
        elif choice == '4':
            print(f"\n{Fore.GREEN}Thank you for using File Integrity Monitor!")
            print(f"{Fore.CYAN}Goodbye!{Style.RESET_ALL}\n")
            break
        
        else:
            print(f"\n{Fore.RED}Invalid choice! Please enter 1-4.")
            input(f"\n{Fore.CYAN}Press Enter to continue...")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Program interrupted by user.")
        print(f"{Fore.GREEN}Goodbye!{Style.RESET_ALL}\n")
    except Exception as e:
        print(f"\n{Fore.RED}Error: {e}{Style.RESET_ALL}")
        input("\nPress Enter to exit...")
