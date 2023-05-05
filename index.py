from src.main import fetch_weekly_free_games
from src.utils import notify_user, parse_game_list, parse_time_str, process_yaml_text, get_yaml_text, save_new_text
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

    message = '\n'.join(parse_game_list(free_games + to_be_free + promotions_games))
    print(message)
    new_yml_str = process_yaml_text(get_yaml_text(),parse_time_str(to_be_free[0]['start_date']))
    save_new_text(new_yml_str)
    #notify_user(title="Epic Weekly Free Games", content=message)


if __name__ == "__main__":
    run()
