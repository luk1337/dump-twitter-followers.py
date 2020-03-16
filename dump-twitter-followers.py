#!/usr/bin/env python3
import json
import requests
import sys

from config import *


def get_followers(user_id: int, cursor: int = -1):
    url = f'https://api.twitter.com/1.1/friends/list.json?include_profile_interstitial_type=1&include_blocking=1&include_blocked_by=1&include_followed_by=1&include_want_retweets=1&include_mute_edge=1&include_can_dm=1&include_can_media_tag=1&skip_status=1&cursor={cursor}&user_id={user_id}&count=20'
    data = json.loads(requests.get(url, headers=REQUEST_HEADERS).content)

    for user in data['users']:
        print(f'https://twitter.com/{user["screen_name"]}')

    if data['next_cursor'] != 0:
        get_followers(user_id, data['next_cursor'])

    return data


def get_user(screen_name: str):
    url = f'https://api.twitter.com/1.1/users/show.json?screen_name={screen_name}'
    data = json.loads(requests.get(url, headers=REQUEST_HEADERS).content)

    return data


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(f'usage: {sys.argv[0]} [screen_name]')

    _, screen_name = sys.argv

    user = get_user(screen_name)
    get_followers(user['id'])
