#!/usr/bin/env python3
import json
import requests
import sys


def get_followers(user_id: int, cursor: int = -1):
    # extract these using your favorite browser's dev tools.
    headers = {
        'x-csrf-token': '',
        'authorization': '',
        'cookie': '',
    }

    url = f'https://api.twitter.com/1.1/friends/list.json?include_profile_interstitial_type=1&include_blocking=1&include_blocked_by=1&include_followed_by=1&include_want_retweets=1&include_mute_edge=1&include_can_dm=1&include_can_media_tag=1&skip_status=1&cursor={cursor}&user_id={user_id}&count=20'
    data = json.loads(requests.get(url, headers=headers).content)

    for user in data['users']:
        print(f'https://twitter.com/{user["screen_name"]}')

    if data['next_cursor'] != 0:
        get_followers(user_id, data['next_cursor'])

    return data


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(f'usage: {sys.argv[0]} [user_id]')

    # btw you can get user_id from http://gettwitterid.com
    _, user_id = sys.argv

    get_followers(user_id)
