#!/usr/bin/env python3
import json
import requests
import sys
import urllib.parse

from config import *


def get_followers(user_id: str):
    cursor = None
    followers = []

    while True:
        get = urllib.parse.urlencode({'variables': json.dumps({
            'userId': user_id,
            'count': 200,
            'cursor': cursor,
            'withHighlightedLabel': False,
            'withTweetQuoteCount': False,
            'includePromotedContent': False,
            'withTweetResult': False,
            'withUserResult': False,
        })})
        url = f'https://api.twitter.com/graphql/0LTpnyHIBKX5Y8YvYJkvvg/Following?{get}'
        data = json.loads(requests.get(url, headers=REQUEST_HEADERS).content)

        for instruction in data['data']['user']['following_timeline']['timeline']['instructions']:
            if instruction['type'] == 'TimelineAddEntries':
                followers += instruction['entries'][:-2]
                cursor = instruction['entries'][-2]['content']['value']

                if cursor == '0|0':
                    break
        else:
            continue

        break

    return followers


def get_user(screen_name: str):
    url = f'https://api.twitter.com/1.1/users/show.json?screen_name={screen_name}'
    data = json.loads(requests.get(url, headers=REQUEST_HEADERS).content)

    return data


def run():
    if len(sys.argv) != 2:
        sys.exit(f'usage: {sys.argv[0]} [screen_name]')

    _, screen_name = sys.argv

    user = get_user(screen_name)
    followers = get_followers(str(user['id']))

    for entry in followers:
        print(f'https://twitter.com/{entry["content"]["itemContent"]["user"]["legacy"]["screen_name"]}')


if __name__ == '__main__':
    run()
