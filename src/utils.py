from onepush import notify
import requests
from ast import literal_eval
import os

# For local test
if os.environ.get('USER_NOTIFIER_1') is None:
    print('Load .env file from local.')
    from dotenv import load_dotenv
    load_dotenv()


def download_img(img_name,image_url):
    response = requests.get(image_url)
    with open(f'./page/images/{img_name}.png', 'wb') as f:
        f.write(response.content)
    print(f'Download {img_name}.png completed ...')
    return True

def get_notifier_list() -> list[str]:
    notifier_key_list = []
    environ = os.environ.copy()
    for var in environ.keys():
        if 'USER_NOTIFIER' in var.upper():
            notifier_key_list.append(environ.get(var))
    return notifier_key_list

def str_to_dict(str: str) -> dict:
    return literal_eval(str.lower().replace('null', 'None') if 'null' in str.lower() else str)

def notify_user(title, content):
    notify_list = get_notifier_list()
    for i in notify_list:
        notifier, key = i.split('#')
        if not notifier or not key:
            print('No notification method configured ...')
            return
        print('Preparing to send notification ...')
        result = str_to_dict(notify(notifier, key=key, title=title, content=content, group='EpicGamesHelper', url = 'https://torcroft.github.io/EpicGamesHelper/').text)
        if (result.get('code') == 200):
            print(f'Message delivered to user ...')

def parse_game_list(game_list:list[dict]):
    msg_list = []
    for game in game_list:
        download_img(game['name'], game['game_thumbnail'])
        match game['status']:
            case 'FREE':
                msg = f"* {game['name']} ({game['price']}) is FREE now, until {game['end_date']} UTC "
            case 'Not free yet':
                msg = f"* {game['name']} ({game['price']}) will be free from {game['start_date']} to {game['end_date']} UTC"
            case 'in Promotion':
                msg = f"* {game['name']} is in promotion ({game['price']} -> {game['price_promo']}) from {game['start_date']} to {game['end_date']} UTC"
            case _:
                pass
        
        msg_list.append(msg)
    return msg_list