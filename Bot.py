import time
import random
import threading
import requests
from bs4 import BeautifulSoup
from pynput import keyboard
import os
import shutil
import sys
from datetime import datetime

# ===== VERSION =====
LOCAL_VERSION = "2.2"

# ===== WEB =====
URL = "https://ff130j.mimo.run"
ELEMENT_ID = "JumpBot_1.0"

# ===== UPDATER =====
VERSION_URL = "https://raw.githubusercontent.com/Bobi394/BotUpdater/main/version.txt"
BOT_URL = "https://raw.githubusercontent.com/Bobi394/BotUpdater/main/Bot.py"

# ===== ORDNER =====
DOWNLOADS = os.path.join(os.path.expanduser("~"), "Downloads")
BOT_PATH = os.path.join(DOWNLOADS, "Bot.py")
BACKUP_PATH = os.path.join(DOWNLOADS, "Bot_backup.py")
LOG_PATH = os.path.join(DOWNLOADS, "bot_log.txt")
CONFIG_PATH = os.path.join(DOWNLOADS, "config.txt")

# ===== STATUS =====
running = False
web_allows = None
controller = keyboard.Controller()

# ===== HILFSFUNKTIONEN =====
def log(text):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {text}"
    print(line)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def parse_version(v):
    return [int(x) for x in v.strip().split(".")]

# ===== CONFIG LADEN =====
def load_config():
    config = {
        "min_delay": 60,
        "max_delay": 180,
        "update_check_seconds": 10,
        "toggle_key": "+"
    }

    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    config[k] = int(v) if v.isdigit() else v

    return config

config = load_config()

# ===== WEBSITE CHECK =====
def check_website():
    global web_allows, running
    last_status = None

    while True:
        try:
            r = requests.get(URL, timeout=5)
            soup = BeautifulSoup(r.text, "html.parser")
            element = soup.find(id=ELEMENT_ID)
            current_status = element and element.text.strip().lower() == "true"
        except:
            current_status = False

        if current_status != last_status:
            last_status = current_status
            web_allows = current_status
            log(f"Webstatus: {'TRUE' if web_allows else 'FALSE'}")

            if running and not web_allows:
                running = False
                log("Bot automatisch gestoppt")

        time.sleep(1)

# ===== AUTO UPDATE =====
def auto_update_loop():
    while True:
        try:
            online_version = requests.get(VERSION_URL, timeout=5).text.strip()

            if parse_version(online_version) > parse_version(LOCAL_VERSION):
                log(f"Update gefunden: {LOCAL_VERSION} → {online_version}")

                if os.path.exists(BOT_PATH):
                    shutil.copy(BOT_PATH, BACKUP_PATH)
                    log("Backup erstellt")

                code = requests.get(BOT_URL, timeout=5).text
                with open(BOT_PATH, "w", encoding="utf-8") as f:
                    f.write(code)

                log("Neue Version geladen – starte neu 🔄")
                os.startfile(BOT_PATH)
                sys.exit()

        except Exception as e:
            log(f"Update-Fehler: {e}")

        time.sleep(config["update_check_seconds"])

# ===== JUMP LOOP MIT COUNTDOWN =====
def jump_loop():
    global running
    while running:
        delay = random.randint(config["min_delay"], config["max_delay"])
        end = time.time() + delay
        log(f"Nächster Sprung in {delay}s")

        while running and time.time() < end:
            rest = int(end - time.time())
            print(f"\r⏱️ Nächster Sprung in {rest:3d}s", end="")
            time.sleep(0.5)

        print(" " * 40, end="\r")

        if running and web_allows:
            controller.press(keyboard.Key.space)
            time.sleep(0.1)
            controller.release(keyboard.Key.space)
            log("Gesprungen 🦎")

# ===== KEY CONTROL =====
def on_press(key):
    global running
    try:
        if key.char == config["toggle_key"]:
            if web_allows:
                running = not running
                if running:
                    log("Bot AKTIV ➕")
                    threading.Thread(target=jump_loop, daemon=True).start()
                else:
                    log("Bot AUS ➖")
            else:
                log("Aktivierung blockiert (Webstatus FALSE)")
    except:
        pass

# ===== START =====
log(f"Bot gestartet | Version {LOCAL_VERSION}")
log("Config geladen")

threading.Thread(target=check_website, daemon=True).start()
threading.Thread(target=auto_update_loop, daemon=True).start()

log("Drücke Taste zum An/Aus schalten")
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()