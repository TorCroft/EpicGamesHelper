from onepush import notify
import requests
from ast import literal_eval
import os
from datetime import datetime
import re

def get_yaml_text() -> str:
    with open(".github\workflows\FetchWeeklyFreeGames.yml", "r") as file:
        return file.read()

def save_new_text(new_content):
    with open(".github\workflows\FetchWeeklyFreeGames.yml","w") as file:
        return file.write(new_content)

def get_cron(text) -> str:
    match = re.search(r"cron: '(.+)'", text)
    if match:
        cron_expr = match.group(1)
        return cron_expr
    else:
        raise "No Match Found"

def datetime_to_cron(datetimevar: datetime):
    minute = str(datetimevar.minute)
    hour = str(datetimevar.hour)
    day = str(datetimevar.day)
    month = str(datetimevar.month)
    weekday = datetimevar.strftime("%a")
    return f"{minute} {hour} {day} {month} {weekday}"


def parse_time_str(time_str: str) -> str:
    '''Parse time based on '%Y-%m-%d %H:%M:%S %Z' format, return GitHub Cron str.'''
    return datetime_to_cron(datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S %Z"))


def process_yaml_text(original_text, new_cron_str):
    print(f"Replace {get_cron(original_text)} with {new_cron_str}.")
    return re.sub(r"cron: '(.+)'", f"cron: '{new_cron_str}'", original_text)

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