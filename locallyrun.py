import requests
import json

def get_offers():
    url = 'https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions?locale=en-US&country=US&allowCountries=US'
    r = requests.get(url)
    return r.json()['data']['Catalog']['searchStore']['elements']

def is_free_offer(offer):
    promotions = offer.get('promotions')
    if not promotions:
        return False

    for entry in promotions.get('promotionalOffers', []):
        for promo in entry.get('promotionalOffers', []):
            if promo['discountSetting']['discountPercentage'] == 0:
                return True

    for entry in promotions.get('upcomingPromotionalOffers', []):
        for promo in entry.get('promotionalOffers', []):
            if promo['discountSetting']['discountPercentage'] == 0:
                return True

    return False

def get_free_games():
    offers = get_offers()
    return [offer for offer in offers if is_free_offer(offer)]

def main():
    free_games = get_free_games()

    if not free_games:
        print("No free games found.")
        return

    print(f"\n🎮 Free Games Found ({len(free_games)}):\n")
    for game in free_games:
        title = game.get('title', 'Unknown Title')
        desc = game.get('description', '')
        print(f"- {title}\n  {desc}\n")

if __name__ == "__main__":
    main()
