#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# openai_function.py - openai functions

# Create: 2023/03/06
import openai
import sys
import time
import logging
import requests

from config import api_key

logger = logging.getLogger('abc')
openai.api_key = api_key


def openai_chat(prompt, max_tokens=400, timeout=(10,60)):
    start = time.time()
    if len(prompt) <= 0:
        return ''

    try:
        response = openai.Completion.create(engine='text-davinci-003',
                                            prompt=prompt,
                                            n=1,
                                            top_p=1,
                                            temperature=0.9,
                                            frequency_penalty=0,
                                            presence_penalty=0.6,
                                            max_tokens=max_tokens,
                                            request_timeout=timeout)

        # logger.debug(response)
        answer = response.choices[0]['text'].strip()
        logger.info('openai_chat {} spand: {}'.format(len(answer), time.time() - start))
    except Exception as e:
        logger.error('openai_chat spand: {} Exception: {}'.format(time.time() - start, e))
        raise(e)
    return answer

g_context = {}
def chatgpt(username, prompt, save=False, max_tokens=2000, timeout=(10,60), p=False):
    start = time.time()

    if len(prompt) <= 0:
        return ''

    answer = ''
    system_ = {'role': 'system', 'content': username}
    user_= {'role': 'user', 'content': prompt}

    try:
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

        messages.append(user_)
        response = openai.ChatCompletion.create(
            model = 'gpt-3.5-turbo',
            messages = messages,
            n = 1,
            temperature=0.9,
            max_tokens=max_tokens,
            request_timeout=timeout)

        answer = response.choices[0].message.content.strip()
        assistant_= {'role': 'assistant', 'content': answer}

        if save == False:
            g_context[username] = []
        g_context[username].append(user_)
        g_context[username].append(assistant_)
        logger.debug(response.usage)
        logger.debug(g_context[username])
        if p:
            print(answer)

        logger.info('chatgpt {} spand: {} total_tokens: {} completion_tokens: {}'.format(len(answer), time.time() - start, response.usage['total_tokens'], response.usage['completion_tokens']))
    except Exception as e:
        logger.error('chatgpt spand: {} Exception: {}'.format(time.time() - start, e))
        raise(e)

    return answer

def chatgpt_stream(username, prompt, save=False, max_tokens=2000, timeout=(10,60), p=False):
    start = time.time()

    if len(prompt) <= 0:
        return ''

    answer = ''
    system_ = {'role': 'system', 'content': 'speek chinese'}
    user_= {'role': 'user', 'content': prompt}
    total_timeout = timeout[0] + timeout[1]
    tokens = 0

    try:
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
        response = openai.ChatCompletion.create(
            model = 'gpt-3.5-turbo',
            messages = messages,
            temperature=0.9,
            max_tokens=max_tokens,
            request_timeout=timeout,
            stream=True)

        for x in response:
            if 'content' in x['choices'][0]['delta']:
                tokens += 1
                answer += x['choices'][0]['delta']['content']
                if p:
                    print(x['choices'][0]['delta']['content'], end='', flush=True)
                if total_timeout > 0 and time.time() - start >= total_timeout:
                    response.close()

        answer = answer.strip()
        assistant_= {'role': 'assistant', 'content': answer}

        if save == False:
            g_context[username] = []
        g_context[username].append(user_)
        g_context[username].append(assistant_)
        logger.debug(g_context[username])
        if p:
            print('')

        logger.info('chatgpt_stream {} spand: {} tokens: {}'.format(len(answer), time.time() - start, tokens))
    except Exception as e:
        logger.error('chatgpt_stream spand: {} Exception: {}'.format(time.time() - start, e))
        raise(e)

    return answer

def gen_image(prompt, filename, size='512x512'):
    try:
        response  = openai.Image.create(
            prompt=prompt,
            n = 1,
            size = size)

        logger.debug(response)
        image_url = response['data'][0]['url']
        image_response = requests.get(image_url)

        with open(filename, 'wb') as f:
            f.write(image_response.content)

    except Exception as e:
        logger.error(e)
        raise(e)

def edit_image(prompt, filename, input_image, mask_image, size='512x512'):
    try:
        response = openai.Image.create_edit(
            image=open(input_image, 'rb'),
            mask=open(mask_image, 'rb'),
            prompt= prompt,
            n=1,
            size=size)

        logger.debug(response)

        image_url = response['data'][0]['url']
        image_response = requests.get(image_url)

        with open(filename, 'wb') as f:
            f.write(image_response.content)
    except Exception as e:
        logger.error(e)
        raise(e)

def variation_image(filename, input_image, size='256x256'):
    try:
        response = openai.Image.create_variation(
            image=open(input_image, 'rb'),
            n=1,
            size=size)

        logger.debug(response)
        image_url = response['data'][0]['url']
        image_response = requests.get(image_url)

        with open(filename, 'wb') as f:
            f.write(image_response.content)
    except Exception as e:
        logger.error(e)
        raise(e)

def speech(audio_file):
    text = None
    try:
        with open(audio_file, 'rb') as f:
            response = openai.Audio.transcribe('whisper-1', f)

        logger.debug(response)
        text = response['text']
    except Exception as e:
        logger.error(e)
        raise(e)

    return text


def test_chatgpt(stream=True):
    try:
        import readline
        import rlcompleter
        readline.parse_and_bind('tab: complete')
    except Exception:
        pass

    while True:
        try:
            prompt = input('Q: ')
        except EOFError:
            return

        if len(prompt) > 0:
            print('A: ', end='', flush=True)
            if stream == True:
                answer = chatgpt_stream('default', prompt, False, p=True)
            else:
                answer = chatgpt('default', prompt, False, p=True)
        print('')

def test_gen_image(size='1024x1024'):
    prompt = 'a monkey'
    filename = 'media/gen_monkey.png'
    gen_image(prompt, filename, size)

def test_edit_image(size='512x512'):
    prompt = 'add a monkey'
    filename = 'media/monkey_edit.png'
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

    edit_image(prompt, filename, input_png, mask_png, size)

def test_variation_image(size='512x512'):
    filename = 'media/panda_variation.png'
    input_png = 'media/panda.png'
    variation_image(filename, input_png, size)

def test_speech():
    audio_file = 'media/abc.mp3'
    text = speech(audio_file)
    print(text)

if __name__ ==  '__main__':
    logging.basicConfig(level=logging.INFO)
    test_chatgpt()
    # test_gen_image('512x512')
    # test_edit_image('512x512')
    # test_variation_image('512x512')
    # test_speech()
