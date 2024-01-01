from src.main import fetch_weekly_free_games, fetch_pinned_games
from src.utils import notify_user, parse_game_list, delete_files, is_notify_time, logger
import json

def run():
    free_games, to_be_free = fetch_weekly_free_games()
    pined_games = fetch_pinned_games()
    game_data = {
        "free_games": free_games,
        "to_be_free": to_be_free,
        "pinned": pined_games
    }
    
    with open("./page/json/game_info.json", "w", encoding='utf-8') as f:
        json.dump(game_data, f)
    
    image_folder = "./page/images"
    delete_files(image_folder)

    message = '\n'.join(parse_game_list(free_games + to_be_free))
    print(message)
    if is_notify_time(free_games[0]['start_date']):
        notify_user(title="Epic Weekly Free Games", content=message)
    else:
        logger.info("Push notification is cancelled ...")

if __name__ == "__main__":
    run()
