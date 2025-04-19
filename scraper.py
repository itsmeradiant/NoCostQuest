import requests, json
from datetime import datetime

URL = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=en-US&country=US"
RAW_PATH = "games.json"
README_PATH = "README.md"

def get_free_games():
    r = requests.get(URL).json()
    games = r["data"]["Catalog"]["searchStore"]["elements"]

    free = []
    for game in games:
        if game['price']['totalPrice']['discountPrice'] == 0:
            title = game['title']
            url = f"https://store.epicgames.com/p/{game['productSlug']}"
            start = game['promotions']['promotionalOffers'][0]['promotionalOffers'][0]['startDate']
            end = game['promotions']['promotionalOffers'][0]['promotionalOffers'][0]['endDate']
            free.append({
                "title": title,
                "url": url,
                "start": start[:10],
                "end": end[:10]
            })
    return free

def update_readme(games):
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    with open(README_PATH, "w") as f:
        f.write("# 🎮 Epic Games Free Games Tracker\n\n")
        f.write(f"Last updated: **{now}**\n\n")
        f.write("## 🆓 Currently Free:\n\n")
        for g in games:
            f.write(f"- [{g['title']}]({g['url']}) – 🗓️ {g['start']} to {g['end']}\n")
        f.write("\n---\n")
        f.write("This list auto-updates every 24h via GitHub Actions.\n")

def update_json(games):
    with open(RAW_PATH, "w") as f:
        json.dump(games, f, indent=2)

def main():
    games = get_free_games()
    update_readme(games)
    update_json(games)

if __name__ == "__main__":
    main()
