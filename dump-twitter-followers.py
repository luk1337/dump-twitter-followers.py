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
        variables = {
            'userId': user_id,
            'count': 200,
            'withHighlightedLabel': False,
            'withTweetQuoteCount': False,
            'includePromotedContent': False,
            'withTweetResult': False,
            'withUserResult': False,
        }

        if cursor is not None:
            variables['cursor'] = cursor

        get = urllib.parse.urlencode({'variables': json.dumps(variables)})
        url = f'https://api.twitter.com/graphql/0LTpnyHIBKX5Y8YvYJkvvg/Following?{get}'
        data = json.loads(requests.get(url, headers=REQUEST_HEADERS).content)

        followers.append(data)

        for instruction in data['data']['user']['following_timeline']['timeline']['instructions']:
            if instruction['type'] == 'TimelineAddEntries':
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


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(f'usage: {sys.argv[0]} [screen_name]')

    _, screen_name = sys.argv

    user = get_user(screen_name)
    followers = get_followers(str(user['id']))

    for data in followers:
        for instruction in data['data']['user']['following_timeline']['timeline']['instructions']:
            if instruction['type'] != 'TimelineAddEntries':
                continue

            for entry in instruction['entries']:
                if entry['content']['entryType'] != 'TimelineTimelineItem':
                    continue

                print(f'https://twitter.com/{entry["content"]["itemContent"]["user"]["legacy"]["screen_name"]}')
