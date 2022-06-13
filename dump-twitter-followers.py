#!/usr/bin/env python3
import contextlib
import json
import os
import re
import sys
import time

import requests

from config import *


def api_call(endpoint: str, variables: dict):
    return requests.post(
        url=f'https://twitter.com/i/api/{endpoint}',
        data=variables,
        headers=REQUEST_HEADERS).json()


def ql_api_call(endpoint: str, params: dict):
    if not hasattr(api_call, 'endpoints'):
        api_call.endpoints = get_ql_api_endpoints()

    for i in range(5):
        ret = requests.get(url=api_call.endpoints[endpoint]["url"],
                           params={k: json.dumps(v) for k, v in params.items()},
                           headers=REQUEST_HEADERS).json()

        with contextlib.redirect_stderr(open(os.devnull, 'w')), contextlib.suppress(KeyError):
            if dict_item_or_fail(ret, 'errors', 0, 'extensions', 'name') == 'TimeoutError':
                time.sleep(5)
                continue

        break

    return ret


def get_ql_api_endpoints():
    api_endpoints = {}

    m = re.search(r'https://abs.twimg.com/responsive-web/client-web(-legacy)?/main.[0-9a-z]+.js',
                  requests.get('https://twitter.com', headers={
                      'user-agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.11 Safari/537.36',
                  }).text)
    m = re.findall(
        r'e.exports={queryId:"([\w-]+)",operationName:"([\w-]+)",operationType:"([\w-]+)",metadata:',
        requests.get(m.group(0)).text)

    for query_id, operation_name, operation_type in m:
        api_endpoints[operation_name] = {
            'query_id': query_id,
            'operation_type': operation_type,
            'url': f'https://api.twitter.com/graphql/{query_id}/{operation_name}'
        }

    return api_endpoints


def dict_item_or_fail(d: dict, *args):
    d_backup = d

    try:
        for key in args:
            d = d[key]
    except KeyError as e:
        print(d or d_backup, file=sys.stderr)
        raise e

    return d


def get_followers(user_id: str):
    cursor = None
    followers = []

    while True:
        data = ql_api_call('Following', {
            'variables': {
                'userId': user_id,
                'count': 200,
                'cursor': cursor,
                'includePromotedContent': False,
                'withSuperFollowsUserFields': True,
                'withDownvotePerspective': False,
                'withReactionsMetadata': False,
                'withReactionsPerspective': False,
                'withSuperFollowsTweetFields': True,
            },
            'features': {
                'dont_mention_me_view_api_enabled': True,
                'interactive_text_enabled': True,
                'responsive_web_uc_gql_enabled': False,
                'vibe_tweet_context_enabled': False,
                'responsive_web_edit_tweet_api_enabled': False,
                'standardized_nudges_for_misinfo_nudges_enabled': False,
                'responsive_web_enhance_cards_enabled': False,
            },
        })

        for instruction in dict_item_or_fail(data, 'data', 'user', 'result', 'timeline', 'timeline', 'instructions'):
            if dict_item_or_fail(instruction, 'type') == 'TimelineAddEntries':
                followers += dict_item_or_fail(instruction, 'entries', slice(None, -2))
                cursor = dict_item_or_fail(instruction, 'entries', -2, 'content', 'value')

                if cursor.startswith('0|'):
                    break
        else:
            continue

        break

    return followers


def get_user(screen_name: str):
    data = ql_api_call('UserByScreenName', {
        'variables': {
            'screen_name': screen_name,
            'withHighlightedLabel': False,
            'withSuperFollowsUserFields': False,
            'withNftAvatar': False,
        },
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
        followers = get_followers(dict_item_or_fail(user, 'data', 'user', 'result', 'rest_id'))
    elif arg == 'print_rest_id':
        user = get_user(value)
        sys.exit(dict_item_or_fail(user, 'data', 'user', 'result', 'rest_id'))
    elif arg == 'rest_id':
        followers = get_followers(value)

    for entry in followers:
        user = dict_item_or_fail(entry, 'content', 'itemContent', 'user_results')
        if 'result' in user and 'legacy' in user['result']:
            print(f'https://twitter.com/{dict_item_or_fail(user, "result", "legacy", "screen_name")}')


if __name__ == '__main__':
    run()
