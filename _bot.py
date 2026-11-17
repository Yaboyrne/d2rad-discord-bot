import os
import time
import html
import requests
from bs4 import BeautifulSoup

RAID_WEBHOOK = os.environ.get("RAID_WEBHOOK_URL")
DUNGEON_WEBHOOK = os.environ.get("DUNGEON_WEBHOOK_URL")
URL = "https://d2rad.com/"

# Afbeeldingen, Exotics, wapens en Armor-bonussen per activiteit
ACTIVITY_DATA = {
    # Raids
    "Last Wish": {
        "image": "https://www.bungie.net/img/destiny_content/pgcr/raid_beanstalk.jpg",
        "exotic": "One Thousand Voices (Fusion Rifle)",
        "loot": "Apex Predator, Nation of Beasts, Chattering Bone, Tyranny of Heaven",
        "armor": "Great Hunt Set"
    },
    "Garden of Salvation": {
        "image": "https://www.bungie.net/img/destiny_content/pgcr/raid_garden_of_salvation.jpg",
        "exotic": "Divinity (Quest)",
        "loot": "Reckless Oracle, Ancient Gospel, Prophet of Doom, Accrued Redemption",
        "armor": "Kentarch 3 Set"
    },
    "Deep Stone Crypt": {
        "image": "https://www.bungie.net/img/destiny_content/pgcr/europa-raid-deep-stone-crypt.jpg",
        "exotic": "Eyes of Tomorrow (Rocket Launcher)",
        "loot": "Commemoration, Succession, Heritage, Trustee, Posterity",
        "armor": "Legacy's Oath Set"
    },
    "Vault of Glass": {
        "image": "https://www.bungie.net/img/destiny_content/pgcr/vault_of_glass.jpg",
        "exotic": "Vex Mythoclast (Fusion Rifle)",
        "loot": "Fatebringer, Found Verdict, Hezen Vengeance, Corrective Measure",
        "armor": "Prime Zealot Set"
    },
    "Vow of the Disciple": {
        "image": "https://www.bungie.net/img/destiny_content/pgcr/raid_nemesis.jpg",
        "exotic": "Collective Obligation (Pulse Rifle)",
        "loot": "Forbearance, Cataclysmic, Submission, Deliverance, Insidious",
        "armor": "Resonant Fury Set"
    },
    "King's Fall": {
        "image": "https://www.bungie.net/img/destiny_content/pgcr/raid_kings_fall.jpg",
        "exotic": "Touch of Malice (Scout Rifle)",
        "loot": "Zaouli's Bane, Smite of Merain, Doom of Chelchis, Defiance of Yasmin",
        "armor": "Darkhollow Set"
    },
    "Root of Nightmares": {
        "image": "https://www.bungie.net/img/destiny_content/pgcr/raid_root_of_nightmares.jpg",
        "exotic": "Conditional Finality (Shotgun)",
        "loot": "Rufus's Fury, Briar's Contempt, Nessa's Oblation, Koraxis's Distress",
        "armor": "Agony Set"
    },
    "Crota's End": {
        "image": "https://www.bungie.net/img/destiny_content/pgcr/crotas_end.jpg",
        "exotic": "Necrochasm (Quest / Oversoul Essence)",
        "loot": "Word of Crota, Abyss Defiant, Song of Ir Yût, Fang of Ir Yût",
        "armor": "Willbreaker Set"
    },
    "Salvation's Edge": {
        "image": "https://www.bungie.net/img/destiny_content/pgcr/raid_splinter.jpg",
        "exotic": "Euphony (Linear Fusion Rifle)",
        "loot": "Nullify, Non-Denouement, Critical Anomaly, Imminence, Summum Bonum",
        "armor": "Promised Set"
    },

    # Dungeons
    "Shattered Throne": {
        "image": "https://www.bungie.net/img/destiny_content/pgcr/dungeon_shattered_throne.jpg",
        "exotic": "Wish-Ender (Quest)",
        "loot": "Retold Tale, Waking Vigil, Tigerspite, Sleepless",
        "armor": "Reverie Dawn Set • Riven's Curse"
    },
    "Pit of Heresy": {
        "image": "https://www.bungie.net/img/destiny_content/pgcr/dungeon_pit_of_heresy.jpg",
        "exotic": "Xenophage (Quest)",
        "loot": "Premonition, Apostate, Blasphemer, Heretic",
        "armor": "Dreambane Set"
    },
    "Prophecy": {
        "image": "https://www.bungie.net/img/destiny_content/pgcr/dungeon_prophecy.jpg",
        "exotic": "Geen (Alleen Legendary loot)",
        "loot": "Prosecutor, Adjudicator, Relentless, Judgment, Sudden Death",
        "armor": "Moonfang-X7 & CODA Sets"
    },
    "Grasp of Avarice": {
        "image": "https://destiny.wiki.gallery/images/thumb/3/32/GraspofAvariceMain.jpg/360px-GraspofAvariceMain.jpg",
        "exotic": "Gjallarhorn (Quest)",
        "loot": "Matador 64, Eyasluna, 1000 Yard Stare, Hero of Ages",
        "armor": "Thorn Armor Set"
    },
    "Duality": {
        "image": "https://www.bungie.net/img/destiny_content/pgcr/dungeon_duality.jpg",
        "exotic": "Heartshadow (Sword)",
        "loot": "Lingering Dread, Unforgiven, Stormchaser, Fixed Odds",
        "armor": "Deep Explorer Set"
    },
    "Spire of the Watcher": {
        "image": "https://www.bungie.net/img/destiny_content/pgcr/dungeon_spire_of_the_watcher.jpg",
        "exotic": "Hierarchy of Needs (Bow)",
        "loot": "Wilderflight, Terminus Horizon, Liminal Vigil, Long Arm",
        "armor": "TM-Earp Custom (Cowboy) Set"
    },
    "Ghosts of the Deep": {
        "image": "https://www.bungie.net/img/destiny_content/pgcr/dungeon_ghosts_of_the_deep.jpg",
        "exotic": "The Navigator (Trace Rifle)",
        "loot": "Cold Comfort, No Survivors, New Pacific Epitaph, Greasy Luck",
        "armor": "Taken King Set"
    },
    "Warlord's Ruin": {
        "image": "https://destiny.wiki.gallery/images/thumb/6/6c/Warlord%27sRuinPromo.jpg/360px-Warlord%27sRuinPromo.jpg",
        "exotic": "Buried Bloodline (Sidearm)",
        "loot": "Indebted Kindness, Vengeful Whisper, Naeem's Lance, Dragoncult Sickle",
        "armor": "Dark Age Set"
    },
    "Vesper's Host": {
        "image": "https://www.bungie.net/img/destiny_content/pgcr/dungeon_vespers_host.jpg",
        "exotic": "Ice Breaker (Sniper Rifle)",
        "loot": "VS Chill Inhibitor, VS Velocity Baton, VS Pyroelectric Propellant",
        "armor": "Spacewalk Set"
    },
    "Sundered Doctrine": {
        "image": "https://www.bungie.net/img/destiny_content/pgcr/dungeon_sundered_doctrine.jpg",
        "exotic": "Finality's Auger (Linear Fusion Rifle)",
        "loot": "Unloved, Unworthy, Unsworn, Unveil",
        "armor": "Flain Set"
    }
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

    for item in items:
        info = ACTIVITY_DATA.get(item, {})
        
        embed = {
            "title": f"{category_label}: {item}",
            "url": URL,
            "color": color,
            "fields": [],
            "footer": {
                "text": "Bron: d2rad.com • Bungie API verified"
            }
        }
        
        if info.get("exotic"):
            embed["fields"].append({
                "name": "✨ Farmable Exotic",
                "value": info["exotic"],
                "inline": False
            })
            
        if info.get("loot"):
            embed["fields"].append({
                "name": "🔫 Important loot",
                "value": info["loot"],
                "inline": False
            })

        if info.get("armor"):
            embed["fields"].append({
                "name": "🛡️ Armor",
                "value": info["armor"],
                "inline": False
            })

        if info.get("image"):
            embed["image"] = {"url": info["image"]}

        payload = {
            "username": username,
            "embeds": [embed]
        }

        res = requests.post(webhook_url, json=payload, timeout=10)
        res.raise_for_status()
        time.sleep(1)

if __name__ == "__main__":
    raids, dungeons = get_d2rad_rotation()
    
    send_discord_cards(
        RAID_WEBHOOK,
        "TWIR - This Week In Raids",
        "⚔️ Active Raid",
        15844367,
        raids
    )
    
    send_discord_cards(
        DUNGEON_WEBHOOK,
        "TWID - This Week In Dungeons",
        "🏰 Active Dungeon",
        3447003,
        dungeons
    )
    print("Alle 4 kaarten met armor-bonus succesvol verzonden!")
