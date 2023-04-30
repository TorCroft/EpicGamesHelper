from onepush import notify
from ast import literal_eval
import os

# For local test
if os.environ.get('USER_NOTIFIER_1') is None:
    print('Load .env file from local.')
    from dotenv import load_dotenv
    load_dotenv()

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
        result = str_to_dict(notify(notifier, key=key, title=title, content=content, group='EpicGamesHelper').text)
        if (result.get('code') == 200):
            print(f'Message delivered to user ...')