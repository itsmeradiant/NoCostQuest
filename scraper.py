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

        if not slug:
            print(f"[!] Skipping {title}: Missing slug")
            continue

        # Merge both active and upcoming offers
        promotions = game.get('promotions', {})
        offers = (
            promotions.get('promotionalOffers', []) +
            promotions.get('upcomingPromotionalOffers', [])
        )

        if not offers or not offers[0].get('promotionalOffers'):
            print(f"[-] Skipping {title}: No active or upcoming promotional offer")
            continue

        offer = offers[0]['promotionalOffers'][0]
        try:
            start = offer['startDate'][:10]
            end = offer['endDate'][:10]
        except (KeyError, IndexError):
            print(f"[!] Skipping {title}: Invalid offer structure")
            continue

        # Allow 0-price or isFree tag (some giveaways don't set discountPrice)
        if price_info == 0 or game.get("isFree"):
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
        content = f.read()

    # Build new table rows
    new_rows = "\n".join(
        f"| {g['title']} | {g['start']} → {g['end']} | [Claim Now]({g['url']}) |"
        for g in games
    )

    # Replace the table section using markers
    start_tag = "<!-- BEGIN_GAMES_TABLE -->"
    end_tag = "<!-- END_GAMES_TABLE -->"

    if start_tag not in content or end_tag not in content:
        raise ValueError("README is missing required table markers.")

    before = content.split(start_tag)[0] + start_tag + "\n"
    after = "\n" + end_tag + content.split(end_tag)[1]
    new_table = "| 🎮 Game | 🗓️ Duration | 🔗 Link |\n|--------|--------------|---------|\n" + new_rows

    # Replace the section between markers
    content = before + new_table + after

    # Replace update date
    today = datetime.utcnow().strftime("%Y-%m-%d")
    content = content.replace("{{UPDATE_DATE}}", today)

    # Write back to README
    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(content)

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
