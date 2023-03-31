#!/usr/bin/env python
# -*- coding: utf-8 -*-

# web_test.py - web_test

# Create: 2023/03/17
import json
import time
import requests
import logging

logger = logging.getLogger('abc')

session = requests.Session()
session.keep_alive = True
session.timeout = 60
session.headers.update({
    'Content-Type': 'application/json'
})

IP = ''

g_context = [ {'role': 'system', 'content': 'your are a good boy!'} ]
def get_response(prompt):
    global g_context
    token_count = 0
    for idx,x in enumerate(reversed(g_context)):
        token_count += len(x['content'])
        if token_count >= 2500:
            begin = len(g_context) - idx + 1
            logger.debug('token_count: {} len: {} idx: {} begin: {}'.format(token_count, len(g_context), idx, begin))
            g_context= g_context[begin:]
            break

    data = {
        'prompt': prompt,
        'context': g_context
    }
    logger.debug(data)
    try:

        response = session.post(f'http://{IP}/web', json=data, stream=True)

        return response
    except Exception as e:
        raise(e)


def run(prompt, save=False):
    global g_context

    try:
        response = get_response(prompt)
        answer = ''
        for x in response:
            data = x.decode('utf-8')
            answer += data
            print(data, flush=True, end='')
        print('')

        if save == False:
            g_context = []
        g_context.append({'role': 'user', 'content': prompt})
        g_context.append({'role': 'assistant', 'content': answer})
    except Exception as e:
        g_context = []
        print('Exception: {}'.format(e))


def test_run():
    try:
        import readline
        import rlcompleter
        readline.parse_and_bind('tab: complete')
    except Exception:
        pass

    while True:
        try:
            prompt = input('Q: ')
        except Exception:
            return

        if len(prompt) > 0:
            print('A: ', end='', flush=True)
            run(prompt, False)
        print('')

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    if len(IP) == 0:
        print("set IP to your server ip")
    else:
        test_run()
