from epicstore_api import EpicGamesStoreAPI
from datetime import datetime, timedelta
import os
import json

IMAGE_ORDER_LIST = [
    "OfferImageTall",
    "Thumbnail",
    "OfferImageWide",
    "DieselStoreFrontWide"
]

RAW_DATA_JSON_PATH = "./page/json/raw_data.json"

def has_discount_zero(item):
    if item.get("promotions") is not None:
        for offer in item["promotions"].get("promotionalOffers", []) + item["promotions"].get("upcomingPromotionalOffers", []):
            if any(offer["discountSetting"]["discountPercentage"] == 0 for offer in offer.get("promotionalOffers", [])):
                return True
    return False


def fetch_weekly_free_games():
    """Fetches current free games from the store."""

    free_games_list = []
    upcoming_free_games_list = []

    api = EpicGamesStoreAPI(country="CN")
    free_games = api.get_free_games()["data"]["Catalog"]["searchStore"]["elements"]

    # Few odd items do not seems game and don't have the promotion attribute, so let's check it !
    free_games = list(sorted(filter(has_discount_zero, free_games), key=lambda g: g["title"]))

    os.makedirs(os.path.dirname(RAW_DATA_JSON_PATH), exist_ok=True)

    with open(RAW_DATA_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(free_games, f, indent=4)

    for game in free_games:
        game_title = game["title"]

        try:
            game_url = f"https://store.epicgames.com/en-US/p/{game['productSlug']}"
            if game["productSlug"] == "[]" or game["productSlug"] is None:
                game_url = "https://store.epicgames.com/en-US/free-games"
        except IndexError:
            game_url = "https://store.epicgames.com/en-US/free-games"

        game_thumbnail_dict = {}
        for image in game["keyImages"]:
            game_thumbnail_dict.update({image["type"]: image["url"]})

        if game_thumbnail_dict:
            for image in IMAGE_ORDER_LIST:
                if image in game_thumbnail_dict:
                    game_thumbnail = game_thumbnail_dict[image]
                    break
        else:
            game_thumbnail = None

        game_price = game["price"]["totalPrice"]["fmtPrice"]["originalPrice"]

        game_promotions = game["promotions"]["promotionalOffers"]
        upcoming_promotions = game["promotions"]["upcomingPromotionalOffers"]

        if game_promotions and game["price"]["totalPrice"]["discountPrice"] == 0:
            # Promotion is active.
            promotion_data = game_promotions[0]["promotionalOffers"][0]

            start_date = datetime.fromisoformat(promotion_data["startDate"][:-1])
            try:
                end_date = datetime.fromisoformat(promotion_data["endDate"][:-1])
            except TypeError:
                end_date = start_date + timedelta(days=7)
            free_games_list.append(
                {
                    "name": game_title,
                    "price": game_price,
                    "status": "FREE",
                    "start_date": f"{start_date} UTC",
                    "end_date": f"{end_date} UTC",
                    "game_thumbnail": game_thumbnail,
                    "link": game_url,
                }
            )
        else:
            # Promotion is not active yet, but will be active soon.
            for promotion in upcoming_promotions[0]["promotionalOffers"]:
                if promotion["discountSetting"]["discountPercentage"] == 0:
                    promotion_data = promotion
                    break

            start_date = datetime.fromisoformat(promotion_data["startDate"][:-1])
            end_date = datetime.fromisoformat(promotion_data["endDate"][:-1])
            upcoming_free_games_list.append(
                {
                    "name": game_title,
                    "price": game_price,
                    "status": "Coming Soon",
                    "start_date": f"{start_date} UTC",
                    "end_date": f"{end_date} UTC",
                    "game_thumbnail": game_thumbnail,
                    "link": game_url,
                }
            )

    return free_games_list, upcoming_free_games_list


def fetch_pinned_games():
    pinned_games = []
    api = EpicGamesStoreAPI(country="CN")
    pinned_game = api.fetch_store_games(count=1, keywords="Black Myth: Wukong")["data"]["Catalog"]["searchStore"]["elements"][0]
    
    game_thumbnail_dict = {}
    for image in pinned_game["keyImages"]:
        game_thumbnail_dict.update({image["type"]: image["url"]})

    if game_thumbnail_dict:
            for image in IMAGE_ORDER_LIST:
                if image in game_thumbnail_dict:
                    game_thumbnail = game_thumbnail_dict[image]
                    break
    else:
        game_thumbnail = None

    pinned_games.append(
        {
            "name": pinned_game["title"],
            "effectiveDate": f'{datetime.fromisoformat(pinned_game["effectiveDate"][:-1])}',
            "original_price": pinned_game["price"]["totalPrice"]["fmtPrice"]["originalPrice"],
            "discont_price": pinned_game["price"]["totalPrice"]["fmtPrice"]["discountPrice"],
            "currency": pinned_game["price"]["totalPrice"]["currencyCode"],
            "game_thumbnail": game_thumbnail,
            "link": "https://store.epicgames.com/en-US/p/black-myth-wukong-87a72b",
        }
    )

    return pinned_games
