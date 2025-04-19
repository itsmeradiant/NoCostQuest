import requests
import json
from datetime import datetime

API_URL = "https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions?locale=en-US&country=US&allowCountries=US"
GAMES_JSON = "games.json"
README_FILE = "README.md"

def fetch_games():
    resp = requests.get(API_URL)
    data = resp.json()

    all_games = data["data"]["Catalog"]["searchStore"]["elements"]
    free_games = []

    for game in all_games:
        title = game.get("title")
        description = game.get("description", "").replace("\n", " ").strip()

        promotions = game.get("promotions", {})
        current = promotions.get("promotionalOffers", [])
        upcoming = promotions.get("upcomingPromotionalOffers", [])

        if current:
            promo = current[0]["promotionalOffers"][0]
        elif upcoming:
            promo = upcoming[0]["promotionalOffers"][0]
        else:
            continue  # No promotion found, skip

        if promo["discountSetting"]["discountPercentage"] != 0:
            continue  # Not 100% off

        start = promo["startDate"]
        end = promo["endDate"]

        slug = game.get("productSlug") or (
            game.get("offerMappings", [{}])[0].get("pageSlug", "")
        )
        url = f"https://store.epicgames.com/en-US/p/{slug}" if slug else "https://store.epicgames.com/"

        free_games.append({
            "title": title,
            "description": description,
            "startDate": start,
            "endDate": end,
            "url": url,
        })

    return free_games

def update_json(games):
    with open(GAMES_JSON, "w", encoding="utf-8") as f:
        json.dump(games, f, indent=2)
    print(f"[✓] Saved {len(games)} entries to {GAMES_JSON}")

def update_readme(games):
    with open(README_FILE, "r", encoding="utf-8") as f:
        readme = f.read()

    table = "| 🎮 Game | 🗓️ Duration | 🔗 Link |\n|--------|--------------|---------|\n"
    for g in games:
        start = datetime.fromisoformat(g["startDate"].replace("Z", "+00:00")).strftime("%b %d")
        end = datetime.fromisoformat(g["endDate"].replace("Z", "+00:00")).strftime("%b %d")
        duration = f"{start} - {end}"
        table += f"| {g['title']} | {duration} | [Link]({g['url']}) |\n"

    updated = readme.split("<!-- BEGIN_GAMES_TABLE -->")[0] + \
              "<!-- BEGIN_GAMES_TABLE -->\n" + \
              table + \
              "<!-- END_GAMES_TABLE -->" + \
              readme.split("<!-- END_GAMES_TABLE -->")[1]

    updated = updated.replace(
        "Last updated: 2025-04-19", f"Last updated: {datetime.utcnow().strftime('%Y-%m-%d')}"
    )

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(updated)
    
    print(f"[✓] README updated with {len(games)} games.")

def main():
    print("🚀 Fetching free games from Epic Games...")
    games = fetch_games()
    update_json(games)
    update_readme(games)

    print(f"\n🎮 Free Games Found ({len(games)}):\n")
    for g in games:
        print(f"- {g['title']}\n  {g['description']}\n")

if __name__ == "__main__":
    main()
