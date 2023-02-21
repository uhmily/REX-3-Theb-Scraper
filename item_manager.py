import json
import os


def get_bot_token():
    return os.getenv("BOT_TOKEN")


def get_auth_token():
    return os.getenv("ZETEX_TOKEN")


def get_tracker_bots():
    with open("info.json", "r") as f:
        return json.load(f)['TRACKER_BOTS']


def get_color_names():
    with open("color_names.json", "r") as f:
        return json.load(f)


def get_theb_dict():
    with open("theb_names.json", "r") as f:
        return json.load(f)

def get_zetex_dict():
    with open("zetex_names.json", "r") as f:
        return json.load(f)
    
def get_username(oldname, channelId):
    if channelId == 0:
        with open("zetex_names.json", "r") as f:
            data = json.load(f)
            if oldname in data:
                return data[oldname]
            return oldname
    if channelId == 1:
        with open("theb_names.json", "r") as f:
            data = json.load(f)
            if oldname in data:
                return data[oldname]
            return oldname

def get_channel(channel):
    with open("info.json", "r") as f:
        return json.load(f)[channel]

def is_testing():
    with open("info.json", "r") as f:
        return json.load(f)['TESTING']
