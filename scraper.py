import requests
import json
from datetime import datetime

URL = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=en-US&country=US&allowCountries=US"
README_PATH = "README.md"
DATA_PATH = "games.json"

def get_free_games():
    print("[*] Fetching data from Epic Games...")
    r = requests.get(URL)
    data = r.json()

    games = data["data"]["Catalog"]["searchStore"]["elements"]
    free = []

    for game in games:
        title = game.get('title', 'Unknown')
        slug = game.get('productSlug', '')
        price_info = game.get('price', {}).get('totalPrice', {}).get('discountPrice', None)

        if not slug or price_info is None:
            print(f"[!] Skipping {title}: Missing slug or price info")
            continue

        # Validate promotions
        promotions = game.get('promotions', {})
        offers = promotions.get('promotionalOffers', [])

        if not offers or not offers[0].get('promotionalOffers'):
            print(f"[-] Skipping {title}: No active promotional offer")
            continue

        offer = offers[0]['promotionalOffers'][0]
        try:
            start = offer['startDate'][:10]
            end = offer['endDate'][:10]
        except (KeyError, IndexError):
            print(f"[!] Skipping {title}: Invalid offer structure")
            continue

        if price_info == 0:
            free.append({
                "title": title,
                "url": f"https://store.epicgames.com/p/{slug}",
                "start": start,
                "end": end
            })
            print(f"[+] Found free game: {title} ({start} → {end})")

    return free

def update_readme(games):
    with open(README_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    start_idx = lines.index("| 🎮 Game | 🗓️ Duration | 🔗 Link |\n") + 2
    end_idx = next((i for i, line in enumerate(lines[start_idx:], start=start_idx) if line.strip().startswith("---")), len(lines))

    # Build new game table rows
    new_rows = [f"| {g['title']} | {g['start']} → {g['end']} | [Claim Now]({g['url']}) |\n" for g in games]

    # Update date placeholder
    today = datetime.utcnow().strftime("%Y-%m-%d")
    for i, line in enumerate(lines):
        if "{{UPDATE_DATE}}" in line:
            lines[i] = line.replace("{{UPDATE_DATE}}", today)

    # Rebuild README
    lines[start_idx:end_idx] = new_rows
    with open(README_PATH, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f"[✓] README updated with {len(games)} games.")

def save_json(games):
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(games, f, indent=2)
    print(f"[✓] Saved {len(games)} entries to {DATA_PATH}")

def main():
    games = get_free_games()
    update_readme(games)
    save_json(games)

if __name__ == "__main__":
    main()
