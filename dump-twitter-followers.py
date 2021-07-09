#!/usr/bin/env python3
import json
import re
import requests
import sys
import urllib.parse

from config import *


def api_call(endpoint: str, variables: dict):
    return json.loads(requests.post(
        url=f'https://twitter.com/i/api/{endpoint}',
        data=variables,
        headers=REQUEST_HEADERS).content)


def ql_api_call(endpoint: str, variables: dict):
    if not hasattr(api_call, 'endpoints'):
        api_call.endpoints = get_ql_api_endpoints()

    return json.loads(requests.get(
        url=api_call.endpoints[endpoint]['url'] + '?' + urllib.parse.urlencode({'variables': json.dumps(variables)}),
        headers=REQUEST_HEADERS).content)


def get_ql_api_endpoints():
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
        data = ql_api_call('Following', {
            'userId': user_id,
            'count': 200,
            'cursor': cursor,
            'withHighlightedLabel': False,
            'withTweetQuoteCount': False,
            'includePromotedContent': False,
            'withTweetResult': True,
            'withReactions': False,
            'withSuperFollowsTweetFields': False,
            'withSuperFollowsUserFields': False,
            'withUserResults': False,
            'withNonLegacyCard': True,
            'withBirdwatchPivots': False,
        })

        for instruction in data['data']['user']['result']['timeline']['timeline']['instructions']:
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
    data = ql_api_call('UserByScreenNameWithoutResults', {
        'screen_name': screen_name,
        'withHighlightedLabel': False,
        'withSuperFollowsUserFields': False,
    })

    return data


def friendships_create(id: str):
    data = api_call('1.1/friendships/create.json', {
        'include_profile_interstitial_type': 1,
        'include_blocking': 1,
        'include_blocked_by': 1,
        'include_followed_by': 1,
        'include_want_retweets': 1,
        'include_mute_edge': 1,
        'include_can_dm': 1,
        'include_can_media_tag': 1,
        'skip_status': 1,
        'id': id,
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
        sys.exit(user['data']['user']['result']['rest_id'])
    elif arg == 'rest_id':
        followers = get_followers(value)

    for entry in followers:
        user = entry["content"]["itemContent"]["user"]
        if 'legacy' in user:
            print(f'https://twitter.com/{user["legacy"]["screen_name"]}')


if __name__ == '__main__':
    run()
