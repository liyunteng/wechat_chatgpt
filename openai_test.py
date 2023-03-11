#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# test.py - test

# Create: 2023/03/03
import sys
import time
import json
import logging
import requests

from config import api_key

logger = logging.getLogger('abc')

session = requests.Session()
session.keep_alive = True
session.timeout = 60
session.headers.update({
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + api_key,
})

def openai_chat_v2(prompt, max_tokens=400, timeout=(10,60)):
    start = time.time()
    if len(prompt) <= 0:
        return ''

    data = {
        'model': 'text-davinci-003',
        'prompt': prompt,
        'n': 1,
        'top_p': 1,
        'temperature': 0.9,
        'frequency_penalty': 0,
        'presence_penalty': 0.6,
        'max_tokens': max_tokens,
    }

    try:
        response = session.post('https://api.openai.com/v1/completions', json=data, timeout=timeout)

        # logger.info(response.json())
        if not response.ok:
            raise requests.RequestException(response.json()['error']['message'])

        answer = response.json()['choices'][0]['text'].strip()

        logger.info('openai_chat_v2 {} spand: {}'.format(len(answer), time.time() - start))
    except Exception as e:
        logger.error('openai_chat_v2 spand: {} Excpetion: {}'.format(time.time() - start, e))
        raise(e)
    return answer

g_context = {}
def chatgpt_v2(username, prompt, save=False, max_tokens=2000, timeout=(10,60), p=False):
    start = time.time()

    if len(prompt) <= 0:
        return ''

    answer = ''
    system_ = {'role': 'system', 'content': username}
    user_= {'role': 'user', 'content': prompt}

    if username not in g_context:
        g_context[username] = [system_]

    messages = g_context[username].copy()

    # TODO: optimiz token_count
    token_count = 0
    for idx,x in enumerate(reversed(messages)):
        token_count += len(x['content'])
        if token_count >= 2500:
            begin = len(messages) - idx + 1
            logger.debug('token_count: {} len: {} idx: {} begin: {}'.format(token_count, len(messages), idx, begin))
            messages = messages[begin:]
            break
        logger.error('answer: {}'.format(answer))

    messages.append(user_)
    data = {
        'model': 'gpt-3.5-turbo',
        'messages': messages,
        'n': 1,
        'temperature': 0.9,
        'max_tokens': max_tokens,
    }

    try:
        response = session.post('https://api.openai.com/v1/chat/completions', json=data, timeout=timeout)

        # logger.info(response.json())
        if not response.ok:
            raise requests.RequestException(response.json()['error']['message'])

        answer = response.json()['choices'][0]['message']['content'].strip()
        assistant_= {'role': 'assistant', 'content': answer}

        if save == False:
            g_context[username] = []
        g_context[username].append(user_)
        g_context[username].append(assistant_)
        logger.debug(response.json()['usage'])
        logger.debug(g_context[username])
        if p:
            print(answer)

        logger.info('chatgpt_v2 {} spand: {} total_tokens: {} completion_tokens: {}'.format(len(answer), time.time() - start, response.json()['usage']['total_tokens'], response.json()['usage']['completion_tokens']))
    except Exception as e:
        logger.error('chatgpt_v2 spand: {} Exception: {}'.format(time.time() - start, e))
        raise(e)

    return answer

def chatgpt_stream_v2(username, prompt, save=False, max_tokens=2000, timeout=(10,60), p=False):
    start = time.time()

    if len(prompt) <= 0:
        return ''

    answer = ''
    system_ = {'role': 'system', 'content': username}
    user_= {'role': 'user', 'content': prompt}
    total_timeout = timeout[0] + timeout[1]
    tokens = 0

    if username not in g_context:
        g_context[username] = [system_]

    messages = g_context[username].copy()

    # TODO: optimiz token_count
    token_count = 0
    for idx,x in enumerate(reversed(messages)):
        token_count += len(x['content'])
        if token_count >= 2000:
            begin = len(messages) - idx + 1
            logger.debug('token_count: {} len: {} idx: {} begin: {}'.format(token_count, len(messages), idx, begin))
            messages = messages[begin:]
            break

    messages.append(user_)
    data = {
        'model': 'gpt-3.5-turbo',
        'messages': messages,
        'temperature': 0.9,
        'max_tokens': max_tokens,
        'stream': True,
    }

    try:
        response = session.post('https://api.openai.com/v1/chat/completions', json=data, stream=True, timeout=timeout)

        # logger.info(response.json())
        if not response.ok:
            raise requests.RequestException(response.json()['error']['message'])

        # print(response.text)
        for x in response.iter_lines(delimiter=b'\n\n'):
            if len(x) < 20:
                continue
            data = json.loads(x[6:])
            if 'content' in data['choices'][0]['delta']:
                tokens += 1
                answer += data['choices'][0]['delta']['content']
                if p:
                    print(data['choices'][0]['delta']['content'], end='', flush=True)
                if total_timeout > 0 and time.time() - start >= total_timeout:
                    response.close()
                    break

        answer = answer.strip()
        assistant_= {'role': 'assistant', 'content': answer}

        if save == False:
            g_context[username] = []
        g_context[username].append(user_)
        g_context[username].append(assistant_)
        logger.debug(g_context[username])
        if p:
            print('')

        logger.info('chatgpt_stream_v2 {} spand: {} tokens: {}'.format(len(answer), time.time() - start, tokens))
    except Exception as e:
        logger.error('chatgpt_stream_v2 spand: {} Exception: {}'.format(time.time() - start, e))
        raise(e)

    return answer

def gen_image_v2(prompt, filename, size='512x512'):
    model = 'image-alpha-001'
    data = {
        'model': model,
        'prompt': prompt,
        'n': 1,
        'size': size,
        'response_format': 'url',
    }

    try:
        response = session.post('https://api.openai.com/v1/images/generations', json=data)
        if not response.ok:
            raise requests.RequestException(response.json()['error']['message'])

        image_url = response.json()['data'][0]['url']
        image_response = requests.get(image_url)

        if not image_response.ok:
            raise requests.RequestException(f'{image_response.status_code}: {image_response.content}')

        with open(filename, 'wb') as f:
            f.write(image_response.content)
    except Exception as e:
        logger.error(e)
        raise(e)

def edit_image_v2(prompt, filename, input_image, mask_image, size='512x512'):
    model = 'image-alpha-001'
    data = {
        'model': model,
        'prompt': prompt,
        'n': 1 ,
        'size': size,
        'response_format': 'url',
    }

    files = {
        'image': (input_image, open(input_image, 'rb')),
        'mask': (mask_image, open(mask_image, 'rb')),
    }

    headers = {
        'Authorization': 'Bearer ' + api_key,
    }

    try:
        data, content_type = requests.models.RequestEncodingMixin._encode_files(
           files, data
        )
        headers['Content-Type'] = content_type
        response = session.post('https://api.openai.com/v1/images/edits', data=data, headers=headers)
        if not response.ok:
            raise requests.RequestException(response.json()['error']['message'])

        image_url = response.json()['data'][0]['url']
        image_response = requests.get(image_url)
        if not image_response.ok:
            raise requests.RequestException(f'{image_response.status_code}: {image_response.content}')

        with open(filename, 'wb') as f:
            f.write(image_response.content)

    except Exception as e:
        logger.error(e)
        raise(e)

def variation_image_v2(filename, input_image, size='256x256'):
    model = 'image-alpha-001'
    data = {
        'model': model,
        'n': 1,
        'size': size,
        'response_format': 'url',
    }

    files = {
        'image': (input_image, open(input_image, 'rb'))
    }

    headers = {
        'Authorization': 'Bearer ' + api_key,
    }


    try:
        data, content_type = requests.models.RequestEncodingMixin._encode_files(
           files, data
        )
        headers['Content-Type'] = content_type

        response = session.post('https://api.openai.com/v1/images/variations', data=data, headers=headers)
        if not response.ok:
            raise requests.RequestException(response.json()['error']['message'])

        image_url = response.json()['data'][0]['url']
        image_response = requests.get(image_url)
        if not image_response.ok:
            raise requests.RequestException(f'{image_response.status_code}: {image_response.content}')

        with open(filename, 'wb') as f:
            f.write(image_response.content)
    except Exception as e:
        logger.error(e)
        raise(e)

def speech_v2(audio_file):
    text = None
    model = 'whisper-1'

    data = {
        'model': model,
    }

    files = {
        'file': (audio_file, open(audio_file, 'rb'))
    }

    headers = {
        'Authorization': 'Bearer ' + api_key,
    }

    try:
        data, content_type = requests.models.RequestEncodingMixin._encode_files(
           files, data
        )
        headers['Content-Type'] = content_type

        response = session.post('https://api.openai.com/v1/audio/transcriptions', data=data, headers=headers)
        if not response.ok:
            raise requests.RequestException(response.json()['error']['message'])

        text = response.json()['text']
    except Exception as e:
        logger.error(e)
        raise(e)

    return text


def test_chatgpt_v2(stream=True):
    while True:
        prompt = input('Q: ')
        if len(prompt) > 0:
            print('A: ', end='', flush=True)
            if stream == True:
                answer = chatgpt_stream_v2('default', prompt, False, p=True)
            else:
                answer = chatgpt_v2('default', prompt, False, p=True)
            print('')
        else:
            break

def test_gen_image_v2(size='1024x1024'):
    prompt = 'a monkey'
    filename = 'media/gen_monkey_v2.png'
    gen_image_v2(prompt, filename, size)

def test_edit_image_v2(size='512x512'):
    prompt = 'add a monkey'
    filename = 'media/monkey_edit_v2.png'
    input_png = 'media/panda_rgba.png'
    mask_png = 'media/mask_rgba.png'
    from PIL import Image
    mask = Image.open(input_png, 'r')
    for h in range(mask.size[1]):
        for w in range(mask.size[0]):
            pix = mask.getpixel((w,h))
            if w > mask.size[0] // 2:
                mask.putpixel((w,h), (0, 0, 0, 0))
    with open(mask_png, 'wb') as f:
        mask.save(f)

    edit_image_v2(prompt, filename, input_png, mask_png, size)

def test_variation_image_v2(size='512x512'):
    filename = 'media/panda_variation_v2.png'
    input_png = 'media/panda.png'
    variation_image_v2(filename, input_png, size)

def test_speech_v2():
    audio_file = 'media/abc.mp3'
    text = speech_v2(audio_file)
    print(text)

if __name__ ==  '__main__':
    logging.basicConfig(level=logging.INFO)
    test_chatgpt_v2()
    # test_gen_image_v2('512x512')
    # test_edit_image_v2('512x512')
    # test_variation_image_v2('512x512')
    # test_speech_v2()



