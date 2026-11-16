import os
import html
import requests
from bs4 import BeautifulSoup

RAID_WEBHOOK = os.environ.get("RAID_WEBHOOK_URL")
DUNGEON_WEBHOOK = os.environ.get("DUNGEON_WEBHOOK_URL")
URL = "https://d2rad.com/"

def get_d2rad_rotation():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    response = requests.get(URL, headers=headers, timeout=15)
    response.raise_for_status()
    
    # Zet HTML-codes zoals ' direct om naar gewone apostroffen
    clean_html = html.unescape(response.text)
    soup = BeautifulSoup(clean_html, "html.parser")
    
    text = soup.get_text("\n", strip=True)
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    raids = []
    dungeons = []
    mode = None

    for line in lines:
        upper = line.upper()
        if upper == "THIS WEEK":
            mode = "START"
            continue
        if mode == "START" and upper == "RAIDS":
            mode = "RAIDS"
            continue
        elif mode == "RAIDS" and upper == "DUNGEONS":
            mode = "DUNGEONS"
            continue
        elif mode == "DUNGEONS" and ("RESET INFORMATION" in upper or "NEXT WEEK" in upper):
            break

        if line not in ["Bungie API verified", "Loot", "✓"]:
            if mode == "RAIDS" and len(raids) < 2:
                raids.append(line)
            elif mode == "DUNGEONS" and len(dungeons) < 2:
                dungeons.append(line)

    return raids, dungeons

def send_discord_message(webhook_url, username, title, color, items):
    if not webhook_url:
        raise ValueError(f"Webhook URL ontbreekt voor {title}!")

    description = "\n".join([f"• **{item}**" for item in items]) if items else "Geen data gevonden"

    payload = {
        "username": username,
        "embeds": [
            {
                "title": title,
                "url": URL,
                "color": color,
                "description": description,
                "footer": {
                    "text": "Bron: d2rad.com • Bungie API verified"
                }
            }
        ]
    }

    res = requests.post(webhook_url, json=payload, timeout=10)
    res.raise_for_status()

if __name__ == "__main__":
    raids, dungeons = get_d2rad_rotation()
    
    send_discord_message(
        RAID_WEBHOOK,
        "Destiny 2 Raid Rotatie",
        "⚔️ Wekelijkse Raid Rotatie",
        15844367,
        raids
    )
    
    send_discord_message(
        DUNGEON_WEBHOOK,
        "Destiny 2 Dungeon Rotatie",
        "🏰 Wekelijkse Dungeon Rotatie",
        3447003,
        dungeons
    )
    print("Beide berichten succesvol verzonden!")
