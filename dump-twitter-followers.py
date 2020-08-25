#!/usr/bin/env python3
import json
import re
import requests
import sys
import urllib.parse

from config import *

API_ENDPOINTS = {}


def api_call(endpoint: str, variables: dict):
    global API_ENDPOINTS

    return json.loads(requests.get(
        url=API_ENDPOINTS[endpoint]["url"] + '?' + urllib.parse.urlencode({'variables': json.dumps(variables)}),
        headers=REQUEST_HEADERS).content)


def get_followers(user_id: str):
    cursor = None
    followers = []

    while True:
        data = api_call('Following', {
            'userId': user_id,
            'count': 200,
            'cursor': cursor,
            'withHighlightedLabel': False,
            'withTweetQuoteCount': False,
            'includePromotedContent': False,
            'withTweetResult': False,
            'withUserResult': False,
        })

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
    data = api_call('UserByScreenName', {
        'screen_name': screen_name,
        'withHighlightedLabel': False,
    })

    return data


def set_api_endpoints():
    global API_ENDPOINTS

    m = re.search(r'https://abs.twimg.com/responsive-web/client-web-legacy/main.[0-9a-z]+.js',
                  requests.get('https://twitter.com').text)
    m = re.findall(
        r'e.exports={queryId:"([\w-]+)",operationName:"([\w-]+)",operationType:"([\w-]+)"}',
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
