#!/usr/bin/env python3
import json
import requests
import sys

from config import *


def get_followers(user_id: int):
    cursor = -1
    followers = []

    while True:
        url = f'https://api.twitter.com/1.1/friends/list.json?user_id={user_id}&cursor={cursor}'
        data = json.loads(requests.get(url, headers=REQUEST_HEADERS).content)

        followers.append(data)

        if data['next_cursor'] == 0:
            break

        cursor = data['next_cursor']

    return followers


def get_user(screen_name: str):
    url = f'https://api.twitter.com/1.1/users/show.json?screen_name={screen_name}'
    data = json.loads(requests.get(url, headers=REQUEST_HEADERS).content)

    return data


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(f'usage: {sys.argv[0]} [screen_name]')

    _, screen_name = sys.argv

    user = get_user(screen_name)
    followers = get_followers(user['id'])
    urls = []

    for data in followers:
        for user in data["users"]:
            url = f'https://twitter.com/{user["screen_name"]}'

            if url not in urls:
                urls.append(url)

    print('\n'.join(urls))
