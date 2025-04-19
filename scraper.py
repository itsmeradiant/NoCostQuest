import json
import requests
from datetime import datetime

# API URL for fetching free games data
URL = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=en-US&country=US&allowCountries=US"
README_PATH = "README.md"
DATA_PATH = "games.json"
DISCORD_WEBHOOK_URL = "YOUR_DISCORD_WEBHOOK_URL"  # Replace with your actual webhook
HISTORY_FILENAME = "history.txt"

def load_previous_games():
    """Load previously found games from history file."""
    try:
        with open(HISTORY_FILENAME, "r") as f:
            return f.read().splitlines()
    except FileNotFoundError:
        return []

def save_history(new_games):
    """Save the new games to the history file."""
    with open(HISTORY_FILENAME, "w") as f:
        f.write("\n".join(new_games))

def send_to_discord(game):
    """Send a notification to Discord when a new game is found."""
    data = {
        "embeds": [{
            "title": f"New Free Game: {game['title']}",
            "description": game.get('description', 'No description available'),
            "url": game['url'],
            "image": {
                "url": game['image']
            },
            "footer": {
                "text": "Epic Games Free Games Alert"
            }
        }]
    }
    response = requests.post(DISCORD_WEBHOOK_URL, json=data)
    if response.status_code == 204:
        print(f"[✓] Sent Discord notification for {game['title']}")
    else:
        print(f"[!] Failed to send Discord notification for {game['title']}")

def get_free_games():
    """Fetch the free games from the Epic Games Store API."""
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
                "end": end,
                "image": game.get('keyImages', [{}])[1].get('url', 'https://example.com/default_image.jpg'),
                "description": game.get('description', 'No description available')
            })
            print(f"[+] Found free game: {title} ({start} → {end})")

    return free

def update_readme(games):
    """Update the README file with the list of free games."""
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

def main():
    """Main function to handle the script flow."""
    games = get_free_games()
    
    # Load previous games from history
    previous_game_names = load_previous_games()
    
    # Filter out games that were already in the history
    new_games = [game for game in games if game['title'] not in previous_game_names]

    # Notify via Discord and update README
    if new_games:
        for game in new_games:
            send_to_discord(game)

        update_readme(new_games)
        save_history([game['title'] for game in new_games])  # Update history

if __name__ == "__main__":
    main()
