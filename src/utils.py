from datetime import datetime, timezone,timedelta
from onepush import notify
from loguru import logger
from ast import literal_eval
import numpy as np
import cv2
import os
import requests
import re

def cv_imread(file_path=""):
    img_mat = cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), -1)
    return img_mat

def cv_imwrite(file_path, frame):
    cv2.imencode('.png', frame)[1].tofile(file_path)

def resize_image(image_folder_path):
    for i in os.listdir(image_folder_path):
        image_path = os.path.join(image_folder_path, i)
        img = cv_imread(image_path)
        resized_img = cv2.resize(img, (375, 500))
        if cv2.imwrite(f"{image_path}", resized_img) is False:
            logger.info(f"Use numpy read image [{i}]")
            cv_imwrite(image_path, resized_img)
        logger.info(f"Resized {i} to 375*500")

def is_notify_time(datetime_str:str):
    date_obj = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S %Z').replace(tzinfo=timezone.utc)
    today = datetime.now(timezone.utc)
    return date_obj <= today and today < date_obj + timedelta(hours=2)

def delete_files(path):
    """
    删除指定路径下的所有文件
    """
    dir_list = os.listdir(path)
    if len(dir_list)==0:
        return
    # 遍历文件夹中的所有文件和子文件夹
    for file in dir_list:
        full_path = os.path.join(path, file)
        # 判断是否为文件，如果是则删除
        if os.path.isfile(full_path):
            os.remove(full_path)
            print(f"删除{full_path} ...")
        # 如果是文件夹，则递归调用本函数
        elif os.path.isdir(full_path):
            delete_files(full_path)


# For local test
if os.environ.get('USER_NOTIFIER_1') is None:
    print('Load .env file from local.')
    from dotenv import load_dotenv
    load_dotenv()


def download_img(img_name,image_url):
    if image_url is None:
        return False
    try:
        response = requests.get(image_url)
    except requests.exceptions.RequestException as e:
        print(f"Download Failed because {e}")
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
                msg = f"* {game['name']} ({game['price']}) is FREE now, until {game['end_date']}"
            case 'Not free yet':
                msg = f"* {game['name']} ({game['price']}) will be free from {game['start_date']} to {game['end_date']}"
            case 'in Promotion':
                msg = f"* {game['name']} is in promotion ({game['price']} -> {game['price_promo']}) from {game['start_date']} to {game['end_date']}"
            case _:
                pass
        msg_list.append(msg)
    return msg_list