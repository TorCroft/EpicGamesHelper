from src.main import fetch_weekly_free_games
from src.utils import notify_user


def run():
    message_list = fetch_weekly_free_games()
    message = '\n'.join(message_list)
    notify_user(title="", content=message)

if __name__ == "__main__":
    run()