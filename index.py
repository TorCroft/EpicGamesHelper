from src.main import fetch_weekly_free_games
from src.utils import notify_user, parse_game_list, delete_files, resize_image, is_notify_time, logger
import json

def run():
    free_games, to_be_free, promotions_games = fetch_weekly_free_games()

    game_data = {
        "free_games": free_games,
        "to_be_free": to_be_free,
        "promotions_games": promotions_games
    }
    
    with open("./page/game_info.json", "w") as f:
        json.dump(game_data, f)
    
    image_folder = "./page/images"

    delete_files(image_folder)

    message = '\n'.join(parse_game_list(free_games + to_be_free + promotions_games))

    resize_image(image_folder)
    print(message)
    if is_notify_time(free_games[0]['start_date']):
        notify_user(title="Epic Weekly Free Games", content=message)
    else:
        logger.info("It is not yet time, push notification has been cancelled ...")

if __name__ == "__main__":
    run()
