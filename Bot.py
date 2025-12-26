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
LOCAL_VERSION = "2.6"

# ===== WEB =====
URL = "https://ff130j.mimo.run"
ELEMENT_ID = "JumpBot_1.0"

# ===== UPDATE =====
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
web_allows = False
controller = keyboard.Controller()
start_time = time.time()
last_seen_version = LOCAL_VERSION

# ===== LOG =====
def log(text):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {text}"
    print(line)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line + "\n")

# ===== VERSION VERGLEICH =====
def parse_version(v):
    return [int(x) for x in v.strip().split(".")]

# ===== CONFIG =====
def load_config():
    cfg = {
        "min_delay": 60,
        "max_delay": 180,
        "toggle_key": "+",
        "status_key": "?",
        "update_check_seconds": 1
    }
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    cfg[k] = int(v) if v.isdigit() else v
    return cfg

config = load_config()

# ===== CONFIG WATCH (KEIN SPAM) =====
def watch_config():
    global config
    last = config.copy()
    while True:
        new = load_config()
        if new != last:
            config = new
            log("Config neu geladen ⚙️")
            last = new.copy()
        time.sleep(1)

# ===== WEBSITE CHECK =====
def check_website():
    global web_allows, running
    last = None

    while True:
        ok = False
        try:
            r = requests.get(URL, timeout=5)
            soup = BeautifulSoup(r.text, "html.parser")
            el = soup.find(id=ELEMENT_ID)
            ok = el and el.text.strip().lower() == "true"
        except:
            ok = False

        if ok != last:
            last = ok
            web_allows = ok
            log(f"Webstatus: {'TRUE ✅' if ok else 'FALSE ❌'}")

            if running and not ok:
                running = False
                log("Bot automatisch gestoppt 🛑")

            if not running and ok:
                running = True
                log("Bot automatisch gestartet 🟢")
                threading.Thread(target=jump_loop, daemon=True).start()

        time.sleep(1)

# ===== AUTO UPDATE (GLEICHE KONSOLE) =====
def auto_update_loop():
    global last_seen_version
    while True:
        try:
            online = requests.get(VERSION_URL, timeout=5).text.strip()

            if online != last_seen_version:
                last_seen_version = online

                if parse_version(online) > parse_version(LOCAL_VERSION):
                    log(f"Update gefunden {LOCAL_VERSION} → {online}")

                    if os.path.exists(BOT_PATH):
                        shutil.copy(BOT_PATH, BACKUP_PATH)
                        log("Backup erstellt 📦")

                    code = requests.get(BOT_URL, timeout=5).text
                    with open(BOT_PATH, "w", encoding="utf-8") as f:
                        f.write(code)

                    log("Update fertig – ersetze laufenden Bot 🔄")
                    time.sleep(1)

                    # 🔥 DAS ist der wichtige Teil:
                    os.execv(sys.executable, [sys.executable, BOT_PATH])
        except:
            pass

        time.sleep(config["update_check_seconds"])

# ===== JUMP LOOP =====
def jump_loop():
    global running
    while running:
        delay = random.randint(config["min_delay"], config["max_delay"])
        end = time.time() + delay
        log(f"Nächster Sprung in {delay}s ⏱️")

        while running and time.time() < end:
            rest = int(end - time.time())
            print(f"\r🦎 Sprung in {rest:3d}s", end="")
            time.sleep(0.5)

        print(" " * 40, end="\r")

        if running and web_allows:
            controller.press(keyboard.Key.space)
            time.sleep(0.1)
            controller.release(keyboard.Key.space)
            log("Gesprungen 🦎✨")

# ===== STATUS ANZEIGE =====
def show_status():
    uptime = int(time.time() - start_time)
    h = uptime // 3600
    m = (uptime % 3600) // 60
    s = uptime % 60

    print("\n====== STATUS ======")
    print(f"Version: {LOCAL_VERSION}")
    print(f"Webstatus: {'TRUE' if web_allows else 'FALSE'}")
    print(f"Bot: {'AKTIV' if running else 'AUS'}")
    print(f"Laufzeit: {h:02d}:{m:02d}:{s:02d}")
    print("====================\n")

# ===== KEY CONTROL =====
def on_press(key):
    global running
    try:
        if key.char == config["toggle_key"]:
            running = not running
            log(f"Bot {'AKTIV 🟢' if running else 'AUS 🔴'}")
            if running:
                threading.Thread(target=jump_loop, daemon=True).start()

        if key.char == config["status_key"]:
            show_status()
    except:
        pass

# ===== START =====
log(f"Bot gestartet | Version {LOCAL_VERSION}")
threading.Thread(target=check_website, daemon=True).start()
threading.Thread(target=auto_update_loop, daemon=True).start()
threading.Thread(target=watch_config, daemon=True).start()

with keyboard.Listener(on_press=on_press) as listener:
    listener.join()