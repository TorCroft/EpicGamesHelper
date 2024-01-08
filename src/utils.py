from datetime import datetime, timezone, timedelta
from os import path, makedirs
from onepush import notify
from loguru import logger
from ast import literal_eval
import numpy as np
import cv2
import os
import requests
import re

# For local test
if os.environ.get("USER_NOTIFIER_1") is None:
    logger.info("Load .env file from local.")
    from dotenv import load_dotenv
    load_dotenv()


def is_notify_time(datetime_str: str):
    date_obj = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S %Z").replace(tzinfo=timezone.utc)
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
        if len(dir_list) == 0:
            return
    for file in dir_list:
        full_path = os.path.join(path, file)
        os.remove(full_path)
        logger.info(f"删除{full_path} ...")
    if not os.path.exists(path):
        os.makedirs(path)


def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', r"_", filename)


def read_image_from_bytes(image_bytes):
    image_array = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    return image if image is not None else None


def write_mat_to_file(mat, img_name):
    success, buffer = cv2.imencode(".png", mat)
    if not success:
        raise Exception("Failed to encode image")
    with open(f"./page/images/{img_name}.png", "wb") as file:
        file.write(buffer.tobytes())


def download_img(img_name, image_url):
    if image_url is None:
        return False
    try:
        response = requests.get(image_url)
    except requests.exceptions.RequestException as e:
        logger.error(f"Download Failed because {e}")
        return False
    img_name = sanitize_filename(img_name)
    write_mat_to_file(read_image_from_bytes(response.content), img_name)
    logger.info(f"Download {img_name}.png completed ...")
    return True


def get_notifier_list() -> list[str]:
    notifier_key_list = []
    environ = os.environ.copy()
    for var in environ.keys():
        if "USER_NOTIFIER" in var.upper():
            notifier_key_list.append(environ.get(var))
    return notifier_key_list


def str_to_dict(str: str) -> dict:
    return literal_eval(str.lower().replace("null", "None") if "null" in str.lower() else str)


def notify_user(title, content):
    notify_list = get_notifier_list()
    for i in notify_list:
        notifier, key = i.split("#")
        if not notifier or not key:
            logger.info("No notification method configured ...")
            return
        logger.info("Preparing to send notification ...")
        result = str_to_dict(
            notify(
                notifier,
                key=key,
                title=title,
                content=content,
                group="EpicGamesHelper",
                url="https://torcroft.github.io/EpicGamesHelper/",
            ).text
        )
        if result.get("code") == 200:
            logger.info(f"Message delivered to user ...")


def parse_game_list(game_list: list[dict]):
    msg_list = []
    image_folder = "./page/images"
    if not path.exists(image_folder):
        makedirs(image_folder)
    for game in game_list:
        download_img(game["name"], game["game_thumbnail"])
        if (game["status"] == "FREE"):
            msg = f"* {game['name']} ({game['price']}) is FREE now, until {game['end_date']}"
        else:
            msg = f"* {game['name']} ({game['price']}) will be free from {game['start_date']} to {game['end_date']}"
        msg_list.append(msg)
    return msg_list
