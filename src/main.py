from epicstore_api import EpicGamesStoreAPI
from datetime import datetime


def fetch_weekly_free_games():
    """Fetches current free games from the store."""

    free_games_list = []
    upcoming_fres_games_list = []
    games_in_promotion_list = []
    always_free_games_list = []
    
    api = EpicGamesStoreAPI(country="CN")
    free_games = api.get_free_games()['data']['Catalog']['searchStore']['elements']

    # Few odd items do not seems game and don't have the promotion attribute, so let's check it !
    free_games = list(sorted(
        filter(
            lambda g: g.get('promotions'),
            free_games
        ),
        key=lambda g: g['title']
    ))

    for game in free_games:
        game_title = game['title']
        game_publisher = game['seller']['name']

        try:
            game_url = f"https://store.epicgames.com/en-US/p/{game['productSlug']}"
            if game['productSlug'] == '[]':
                game_url = ""
        except IndexError:
            game_url = ""
        # Can be useful when you need to also show the thumbnail of the game.
        # Like in Discord's embeds for example, or anything else.
        # Here I showed it just as example and won't use it.

        game_thumbnail = None
        for image in game['keyImages']:
            if image['type'] == 'Thumbnail':
                game_thumbnail = image['url']
                break
        
        game_price = game['price']['totalPrice']['fmtPrice']['originalPrice']
        game_price_promo = game['price']['totalPrice']['fmtPrice']['discountPrice']

        game_promotions = game['promotions']['promotionalOffers']
        upcoming_promotions = game['promotions']['upcomingPromotionalOffers']

        if game_promotions and game['price']['totalPrice']['discountPrice'] == 0:
            # Promotion is active.
            promotion_data = game_promotions[0]['promotionalOffers'][0]
            start_date_iso, end_date_iso = promotion_data['startDate'][:-1], promotion_data['endDate'][:-1]
            
            start_date = datetime.fromisoformat(start_date_iso)
            end_date = datetime.fromisoformat(end_date_iso)
            free_games_list.append(
                {
                    "name": game_title,
                    "price": game_price,
                    "status": "FREE",
                    "start_date": f'{start_date} UTC',
                    "end_date": f'{end_date} UTC',
                    'game_thumbnail': game_thumbnail,
                    "link": game_url
                }
            )
            msg = f'* {game_title} ({game_price}) is FREE now, until {end_date} UTC --> {game_url}'
        elif not game_promotions and upcoming_promotions:
            # Promotion is not active yet, but will be active soon.
            promotion_data = upcoming_promotions[0]['promotionalOffers'][0]
            start_date_iso, end_date_iso = promotion_data['startDate'][:-1], promotion_data['endDate'][:-1]
            
            start_date = datetime.fromisoformat(start_date_iso)
            end_date = datetime.fromisoformat(end_date_iso)
            upcoming_fres_games_list.append(
                {
                    "name": game_title,
                    "price": game_price,
                    "status": "Not free yet",
                    "start_date": f'{start_date} UTC',
                    "end_date": f'{end_date} UTC',
                    'game_thumbnail': game_thumbnail,
                    "link": game_url
                }
            )
        elif game_promotions:
            # Promotion is active.
            promotion_data = game_promotions[0]['promotionalOffers'][0]
            start_date_iso, end_date_iso = promotion_data['startDate'][:-1], promotion_data['endDate'][:-1]
            
            start_date = datetime.fromisoformat(start_date_iso)
            end_date = datetime.fromisoformat(end_date_iso)
            games_in_promotion_list.append(
                {
                    "name": game_title,
                    "price": game_price,
                    "price_promo": game_price_promo,
                    "status": "in Promotion",
                    "start_date": f'{start_date} UTC',
                    "end_date": f'{end_date} UTC',
                    'game_thumbnail': game_thumbnail,
                    "link": game_url
                }
            )
    return free_games_list, upcoming_fres_games_list, games_in_promotion_list
