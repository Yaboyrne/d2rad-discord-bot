import os
import time
import html
import requests
from bs4 import BeautifulSoup

RAID_WEBHOOK = os.environ.get("RAID_WEBHOOK_URL")
DUNGEON_WEBHOOK = os.environ.get("DUNGEON_WEBHOOK_URL")
URL = "https://d2rad.com/"

# Gecontroleerde Bungie.net banner-afbeeldingen
ACTIVITY_IMAGES = {
    # Raids
    "Last Wish": "https://www.bungie.net/img/destiny_content/pgcr/raid_beanstalk.jpg",
    "Garden of Salvation": "https://www.bungie.net/img/destiny_content/pgcr/raid_garden_of_salvation.jpg",
    "Deep Stone Crypt": "https://www.bungie.net/img/destiny_content/pgcr/europa-raid-deep-stone-crypt.jpg",
    "Vault of Glass": "https://www.bungie.net/img/destiny_content/pgcr/vault_of_glass.jpg",
    "Vow of the Disciple": "https://www.bungie.net/img/destiny_content/pgcr/raid_nemesis.jpg",
    "King's Fall": "https://www.bungie.net/img/destiny_content/pgcr/kings_fall.jpg",
    "Root of Nightmares": "https://www.bungie.net/img/destiny_content/pgcr/raid_root_of_nightmares.jpg",
    "Crota's End": "https://www.bungie.net/img/destiny_content/pgcr/crotas_end.jpg",
    "Salvation's Edge": "https://www.bungie.net/img/destiny_content/pgcr/raid_splinter.jpg",
    
    # Dungeons
    "Shattered Throne": "https://www.bungie.net/img/destiny_content/pgcr/dungeon_shattered_throne.jpg",
    "Pit of Heresy": "https://www.bungie.net/img/destiny_content/pgcr/dungeon_pit_of_heresy.jpg",
    "Prophecy": "https://www.bungie.net/img/destiny_content/pgcr/dungeon_prophecy.jpg",
    "Grasp of Avarice": "https://www.bungie.net/img/destiny_content/pgcr/dungeon_grasp_of_avarice.jpg",
    "Duality": "https://www.bungie.net/img/destiny_content/pgcr/dungeon_duality.jpg",
    "Spire of the Watcher": "https://www.bungie.net/img/destiny_content/pgcr/dungeon_spire_of_the_watcher.jpg",
    "Ghosts of the Deep": "https://www.bungie.net/img/destiny_content/pgcr/dungeon_ghosts_of_the_deep.jpg",
    "Warlord's Ruin": "https://www.bungie.net/img/destiny_content/pgcr/dungeon_warlords_ruin.jpg",
    "Vesper's Host": "https://www.bungie.net/img/destiny_content/pgcr/dungeon_vespers_host.jpg",
    "Sundered Doctrine": "https://www.bungie.net/img/destiny_content/pgcr/dungeon_sundered_doctrine.jpg"
}

def get_d2rad_rotation():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    response = requests.get(URL, headers=headers, timeout=15)
    response.raise_for_status()
    
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

def send_discord_cards(webhook_url, username, category_label, color, items):
    if not webhook_url:
        raise ValueError(f"Webhook URL ontbreekt voor {category_label}!")

    # Stuur voor elke activiteit een los bericht zodat Discord de foto's niet samenvoegt
    for item in items:
        embed = {
            "title": f"{category_label}: {item}",
            "url": URL,
            "color": color,
            "footer": {
                "text": "Bron: d2rad.com • Bungie API verified"
            }
        }
        
        image_url = ACTIVITY_IMAGES.get(item)
        if image_url:
            embed["image"] = {"url": image_url}

        payload = {
            "username": username,
            "embeds": [embed]
        }

        res = requests.post(webhook_url, json=payload, timeout=10)
        res.raise_for_status()
        time.sleep(1)  # Korte pauze zodat de volgorde in Discord altijd klopt

if __name__ == "__main__":
    raids, dungeons = get_d2rad_rotation()
    
    send_discord_cards(
        RAID_WEBHOOK,
        "Destiny 2 Raid Rotatie",
        "⚔️ Actieve Raid",
        15844367,
        raids
    )
    
    send_discord_cards(
        DUNGEON_WEBHOOK,
        "Destiny 2 Dungeon Rotatie",
        "🏰 Actieve Dungeon",
        3447003,
        dungeons
    )
    print("Alle 4 kaarten succesvol verzonden!")
