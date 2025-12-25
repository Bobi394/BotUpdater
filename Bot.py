import time
import random
import threading
import requests
from bs4 import BeautifulSoup
from pynput import keyboard
import os
import sys

# ===== Webseite & Elemente =====
URL = "https://ff130j.mimo.run"
ELEMENT_ID = "JumpBot_1.0"

# ===== Updater Settings =====
LOCAL_VERSION = "1.0"
VERSION_URL = "https://raw.githubusercontent.com/Bobi394/BotUpdater/main/version.txt"
BOT_URL = "https://raw.githubusercontent.com/Bobi394/BotUpdater/main/Bot.py"
DOWNLOADS = os.path.join(os.path.expanduser("~"), "Downloads")
BOT_PATH = os.path.join(DOWNLOADS, "Bot.py")

# ===== Globale Variablen =====
running = False
web_allows = None
update_status = False
controller = keyboard.Controller()

# ===== Funktionen =====
def check_website():
    global web_allows, running, update_status
    last_status = None
    while True:
        try:
            r = requests.get(URL, timeout=5)
            soup = BeautifulSoup(r.text, "html.parser")
            element = soup.find(id=ELEMENT_ID)

            current_status = element and element.text.strip().lower() == "true"
            current_update = element and element.text.strip().lower() == "update"

        except Exception:
            current_status = False
            current_update = False

        # Statusänderung behandeln
        if current_status != last_status:
            last_status = current_status
            web_allows = current_status
            print(f"\nWebstatus: {'TRUE ✅' if web_allows else 'FALSE ❌'}")

            # Bot automatisch stoppen, wenn FALSE
            if running and not web_allows:
                running = False
                print("Bot automatisch gestoppt wegen FALSE auf der Webseite 🛑")

        # Update-Status prüfen
        if current_update:
            update_status = True
        else:
            update_status = False

        time.sleep(1)

def update_loop():
    global update_status
    while True:
        if update_status:
            print("Neues Update verfügbar! 🔔", end="\r")
            try:
                # Prüfen, ob GitHub Version neuer ist
                online_version = requests.get(VERSION_URL, timeout=5).text.strip()
                if online_version != LOCAL_VERSION:
                    print("\n🔄 Lade neue Bot-Version...")

                    bot_code = requests.get(BOT_URL, timeout=5).text
                    with open(BOT_PATH, "w", encoding="utf-8") as f:
                        f.write(bot_code)

                    print(f"✅ Update geladen in Downloads: {BOT_PATH}")
                    print("🔁 Bitte Bot neu starten")
                    update_status = False  # einmal erledigt
            except Exception as e:
                print("❌ Fehler beim Updater:", e)
        time.sleep(5)

def jump_loop():
    global running
    while running:
        delay = random.randint(60, 180)
        end_time = time.time() + delay

        print(f"Nächster Sprung in {delay}s ⏱️", end="")

        # Countdown in einer Zeile
        while running and time.time() < end_time:
            remaining = int(end_time - time.time())
            print(f"\rVerbleibende Zeit: {remaining:3d}s", end="")
            time.sleep(0.5)

        if running and web_allows:
            controller.press(keyboard.Key.space)
            time.sleep(0.1)
            controller.release(keyboard.Key.space)
            print("\rGesprungen! 🦎🕹️            ")
        elif running and not web_allows:
            print("\rSpringen blockiert ❌           ")

def on_press(key):
    global running
    try:
        if key.char == '+':
            if web_allows:  # Nur wenn TRUE
                running = not running
                if running:
                    print("\nBot AKTIV ➕🦎")
                    threading.Thread(target=jump_loop, daemon=True).start()
                else:
                    print("\nBot AUS ➖🛑")
            else:
                print("\nBot kann nicht aktiviert werden – Webstatus FALSE ❌")
    except:
        pass

# ===== Threads starten =====
threading.Thread(target=check_website, daemon=True).start()
threading.Thread(target=update_loop, daemon=True).start()

print("Drücke + zum An/Aus schalten ➕🦎 (nur wenn TRUE)")
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()