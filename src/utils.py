from datetime import datetime, timezone,timedelta
from onepush import notify
from loguru import logger
from ast import literal_eval
import numpy as np
import cv2
import os
import requests

# For local test
if os.environ.get('USER_NOTIFIER_1') is None:
    logger.info('Load .env file from local.')
    from dotenv import load_dotenv
    load_dotenv()

def cv_imread(file_path="") -> cv2.Mat:
    img_mat = cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), -1)
    return img_mat

def cv_imwrite(file_path, frame):
    cv2.imencode('.png', frame)[1].tofile(file_path)

def resize_image(image_folder_path):
    for i in os.listdir(image_folder_path):
        image_path = os.path.join(image_folder_path, i)
        img = cv_imread(image_path)
        height, width, _ = img.shape
        scale_factor = 375 / width
        resized_img = cv2.resize(img, (int(width * scale_factor), int(height * scale_factor)))
        if cv2.imwrite(f"{image_path}", resized_img) is False:
            logger.info(f"Use numpy read image [{i}]")
            cv_imwrite(image_path, resized_img)
        logger.info(f"Resized {i} to 375 width while maintaining aspect ratio")

def is_notify_time(datetime_str:str):
    date_obj = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S %Z').replace(tzinfo=timezone.utc)
    today = datetime.now(timezone.utc)
    return date_obj <= today and today < date_obj + timedelta(hours=2)

def delete_files(path):
    """
    删除指定路径下的所有文件
    """
    try:
        dir_list = os.listdir(path)
    except FileNotFoundError:
        if not os.path.exists(path):
            os.makedirs(path)
        return
    else:    
        if len(dir_list)==0:
            return
    for file in dir_list:
        full_path = os.path.join(path, file)
        os.remove(full_path)
        logger.info(f"删除{full_path} ...")


def download_img(img_name,image_url):
    if image_url is None:
        return False
    try:
        response = requests.get(image_url)
    except requests.exceptions.RequestException as e:
        logger.error(f"Download Failed because {e}")
        return False
    with open(f'./page/images/{img_name}.png', 'wb') as f:
        f.write(response.content)
    logger.info(f'Download {img_name}.png completed ...')
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
            logger.info('No notification method configured ...')
            return
        logger.info('Preparing to send notification ...')
        result = str_to_dict(notify(notifier, key=key, title=title, content=content, group='EpicGamesHelper', url = 'https://torcroft.github.io/EpicGamesHelper/').text)
        if (result.get('code') == 200):
            logger.info(f'Message delivered to user ...')

def parse_game_list(game_list:list[dict]):
    msg_list = []
    for game in game_list:
        download_img(game['name'], game['game_thumbnail'])
        match game['status']:
            case 'FREE':
                msg = f"* {game['name']} ({game['price']}) is FREE now, until {game['end_date']}"
            case 'Not free yet':
                msg = f"* {game['name']} ({game['price']}) will be free from {game['start_date']} to {game['end_date']}"
            case 'in Promotion':
                msg = f"* {game['name']} is in promotion ({game['price']} -> {game['price_promo']}) from {game['start_date']} to {game['end_date']}"
            case _:
                pass
        msg_list.append(msg)
    return msg_list