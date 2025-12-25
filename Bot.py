import time
import random
import threading
import requests
from bs4 import BeautifulSoup
from pynput import keyboard
import os
import shutil
from datetime import datetime

# ===== VERSION =====
LOCAL_VERSION = "2.0"

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

# ===== STATUS =====
running = False
web_allows = None
update_status = False
controller = keyboard.Controller()

# ===== LOGGING =====
def log(text):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {text}"
    print(line)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line + "\n")

# ===== WEBSITE CHECK =====
def check_website():
    global web_allows, running, update_status
    last_status = None

    while True:
        try:
            r = requests.get(URL, timeout=5)
            soup = BeautifulSoup(r.text, "html.parser")
            element = soup.find(id=ELEMENT_ID)

            text = element.text.strip().lower() if element else ""
            current_status = text == "true"
            current_update = text == "update"

        except Exception:
            current_status = False
            current_update = False

        if current_status != last_status:
            last_status = current_status
            web_allows = current_status
            log(f"Webstatus geändert: {'TRUE' if web_allows else 'FALSE'}")

            if running and not web_allows:
                running = False
                log("Bot automatisch gestoppt (Webstatus FALSE)")

        update_status = current_update
        time.sleep(1)

# ===== UPDATE LOOP =====
def update_loop():
    global update_status
    while True:
        if update_status:
            try:
                online_version = requests.get(VERSION_URL, timeout=5).text.strip()
                if online_version != LOCAL_VERSION:
                    log(f"Update gefunden: {LOCAL_VERSION} → {online_version}")

                    # Backup
                    if os.path.exists(BOT_PATH):
                        shutil.copy(BOT_PATH, BACKUP_PATH)
                        log("Backup erstellt: Bot_backup.py")

                    # Download
                    bot_code = requests.get(BOT_URL, timeout=5).text
                    with open(BOT_PATH, "w", encoding="utf-8") as f:
                        f.write(bot_code)

                    log("Neue Version in Downloads gespeichert")
                    log("Bitte Bot neu starten 🔁")

                    update_status = False
            except Exception as e:
                log(f"Update-Fehler: {e}")
        time.sleep(5)

# ===== JUMP LOOP =====
def jump_loop():
    global running
    while running:
        delay = random.randint(60, 180)
        log(f"Nächster Sprung in {delay} Sekunden")

        end_time = time.time() + delay
        while running and time.time() < end_time:
            time.sleep(0.5)

        if running and web_allows:
            controller.press(keyboard.Key.space)
            time.sleep(0.1)
            controller.release(keyboard.Key.space)
            log("Gesprungen 🦎")
        elif running:
            log("Sprung blockiert (Webstatus FALSE)")

# ===== KEY CONTROL =====
def on_press(key):
    global running
    try:
        if key.char == '+':
            if web_allows:
                running = not running
                if running:
                    log("Bot AKTIVIERT ➕")
                    threading.Thread(target=jump_loop, daemon=True).start()
                else:
                    log("Bot DEAKTIVIERT ➖")
            else:
                log("Aktivierung blockiert (Webstatus FALSE)")
    except:
        pass

# ===== START =====
log(f"Bot gestartet | Version {LOCAL_VERSION}")

threading.Thread(target=check_website, daemon=True).start()
threading.Thread(target=update_loop, daemon=True).start()

log("Drücke + zum An/Aus schalten")
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()