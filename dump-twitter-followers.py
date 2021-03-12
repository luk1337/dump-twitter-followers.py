#!/usr/bin/env python3
import json
import re
import requests
import sys
import urllib.parse

from config import *


def api_call(endpoint: str, variables: dict):
    if not hasattr(api_call, 'endpoints'):
        api_call.endpoints = get_api_endpoints()

    return json.loads(requests.get(
        url=api_call.endpoints[endpoint]['url'] + '?' + urllib.parse.urlencode({'variables': json.dumps(variables)}),
        headers=REQUEST_HEADERS).content)


def get_api_endpoints():
    api_endpoints = {}

    m = re.search(r'https://abs.twimg.com/responsive-web/client-web/main.[0-9a-z]+.js',
                  requests.get('https://twitter.com', headers={
                      'user-agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
                  }).text)
    m = re.findall(
        r'e.exports={queryId:"([\w-]+)",operationName:"([\w-]+)",operationType:"([\w-]+)"}',
        requests.get(m.group(0)).text)

    for query_id, operation_name, operation_type in m:
        api_endpoints[operation_name] = {
            'query_id': query_id,
            'operation_type': operation_type,
            'url': f'https://api.twitter.com/graphql/{query_id}/{operation_name}'
        }

    return api_endpoints


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

                if cursor.startswith('0|'):
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


def run():
    if len(sys.argv) != 3:
        sys.exit(f'usage: {sys.argv[0]} [screen_name|print_rest_id|rest_id] [value]')

    _, arg, value = sys.argv

    if arg == 'screen_name':
        user = get_user(value)
        followers = get_followers(user['data']['user']['rest_id'])
    elif arg == 'print_rest_id':
        user = get_user(value)
        sys.exit(user['data']['user']['rest_id'])
    elif arg == 'rest_id':
        followers = get_followers(value)

    for entry in followers:
        print(f'https://twitter.com/{entry["content"]["itemContent"]["user"]["legacy"]["screen_name"]}')


if __name__ == '__main__':
    run()
