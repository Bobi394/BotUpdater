# ===== Test Bot Version 2.0 mit Updater =====
import requests
import os
import sys

VERSION = "2.0"
VERSION_URL = "https://raw.githubusercontent.com/Bobi394/BotUpdater/refs/heads/main/version.txt"
BOT_URL = "https://raw.githubusercontent.com/Bobi394/BotUpdater/refs/heads/main/Bot.py"

# Downloads-Ordner
DOWNLOADS = os.path.join(os.path.expanduser("~"), "Downloads")
BOT_PATH = os.path.join(DOWNLOADS, "Bot.py")

print("🤖 Test Bot 2.0 gestartet")
print("📦 Version:", VERSION)

# ===== Updater =====
try:
    online_version = requests.get(VERSION_URL, timeout=5).text.strip()
    if online_version != VERSION:
        print("🔄 Update gefunden! Lade neue Version...")
        bot_code = requests.get(BOT_URL, timeout=5).text
        with open(BOT_PATH, "w", encoding="utf-8") as f:
            f.write(bot_code)
        print("✅ Update geladen in Downloads:", BOT_PATH)
        print("🔁 Bitte Bot neu starten")
    else:
        print("✅ Bot ist aktuell")
except Exception as e:
    print("❌ Fehler beim Updater:", e)

print("🔥 UPDATE ERFOLGREICH!")
print("🦎 Ich bin jetzt Bot Version 2.0")
input("Drücke Enter zum Beenden...")
