#!/usr/bin/env python3
import json
import re
import requests
import sys
import urllib.parse

from config import *

API_ENDPOINTS = {}


def get_followers(user_id: str):
    global API_ENDPOINTS

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
        url = f'{API_ENDPOINTS["Following"]["url"]}?{get}'
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
    global API_ENDPOINTS

    get = urllib.parse.urlencode({'variables': json.dumps({
        'screen_name': screen_name,
        'withHighlightedLabel': False,
    })})
    url = f'{API_ENDPOINTS["UserByScreenName"]["url"]}?{get}'
    data = json.loads(requests.get(url, headers=REQUEST_HEADERS).content)

    return data


def set_api_endpoints():
    global API_ENDPOINTS

    m = re.search(r'https://abs.twimg.com/responsive-web/client-web-legacy/main.[0-9a-z]+.js',
                  requests.get('https://twitter.com').text)
    m = re.findall(
        r'e.exports={queryId:"([0-9a-zA-Z_-]+)",operationName:"([0-9a-zA-Z]+)",operationType:"([0-9a-zA-Z]+)"}',
        requests.get(m.group(0)).text)

    for query_id, operation_name, operation_type in m:
        API_ENDPOINTS[operation_name] = {
            'query_id': query_id,
            'operation_type': operation_type,
            'url': f'https://api.twitter.com/graphql/{query_id}/{operation_name}'
        }


def run():
    if len(sys.argv) != 2:
        sys.exit(f'usage: {sys.argv[0]} [screen_name]')

    _, screen_name = sys.argv

    set_api_endpoints()
    user = get_user(screen_name)
    followers = get_followers(user['data']['user']['rest_id'])

    for entry in followers:
        print(f'https://twitter.com/{entry["content"]["itemContent"]["user"]["legacy"]["screen_name"]}')


if __name__ == '__main__':
    run()
