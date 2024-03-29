# -*- coding: utf-8 -*-

import os
import sys
import time
import logging

from weixin_media import Media
from weixin_token import Token
from openai_function import gen_image, variation_image, speech, chatgpt, chatgpt_stream
# from openai_test import chatgpt_stream_v2

logger = logging.getLogger('abc')

g_token = Token()

class Cache():
    def __init__(self):
        self.cache = {}

    def _clean(self):
        now = time.time()
        self.cache = dict(filter(lambda x: x[1]['deadline'] > now, self.cache.items()))
        logger.debug("cache len: {}".format(len(self.cache)))

    def has(self, recvMsg):
        return recvMsg.MsgId in self.cache

    def put(self, recvMsg, value=None, exception=None):
        self._clean()

        if value is None:
            self.cache[recvMsg.MsgId] = {}
            self.cache[recvMsg.MsgId]['timestamp'] = time.time()
            self.cache[recvMsg.MsgId]['deadline'] = time.time() + 14.5
        self.cache[recvMsg.MsgId]['value'] = value
        self.cache[recvMsg.MsgId]['exception'] = exception
        logger.debug('{}'.format(self.cache))
        if exception is not None:
            raise(Exception(exception))

    def get(self, recvMsg):
        if not self.has(recvMsg):
            return None

        if self.cache[recvMsg.MsgId]['value'] is not None:
            return self.cache[recvMsg.MsgId]['value']

        while self.cache[recvMsg.MsgId]['value'] is None and \
                self.cache[recvMsg.MsgId]['exception'] is None and \
                time.time() < self.cache[recvMsg.MsgId]['deadline']:
            time.sleep(0.1)

        if self.cache[recvMsg.MsgId]['value'] is not None:
            return self.cache[recvMsg.MsgId]['value']
        if self.cache[recvMsg.MsgId]['exception'] is not None:
            raise(Exception(self.cache[recvMsg.MsgId]['exception']))
        else:
            logger.error('Timeout: {}'.format(self.cache[recvMsg.MsgId]))
            raise(Exception('Timeout'))


def init_logging(debug=False):
    l = logging.getLogger('abc')
    l.setLevel(logging.DEBUG)


    formatter = logging.Formatter('[%(asctime)s] %(levelname)5s - %(message)s')

    if debug:
        formatter = logging.Formatter('[%(asctime)s] - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

    fh = logging.FileHandler('main.log', mode='w')
    fh.setFormatter(formatter)
    if debug:
        fh.setLevel(logging.DEBUG)

        sh = logging.StreamHandler()
        sh.setFormatter(formatter)
        sh.setLevel(logging.DEBUG)
        l.addHandler(sh)
    else:
        fh.setLevel(logging.INFO)
    l.addHandler(fh)

    return l

def weixin_chatgpt(username, prompt, max_tokens=500, timeout=(2.0, 12.0)):
    answer = None
    try:
        answer = chatgpt_stream(username, prompt, False, max_tokens=max_tokens, timeout=timeout)
    except Exception as e:
        raise(e)
    return answer

def weixin_gen_image(msgId, prompt, size='512x512'):
    mid = None
    try:
        os.mkdir(msgId)
        output_image = os.path.join(msgId, 'output.png')

        gen_image(prompt, output_image, size)
        accessToken = g_token.get_access_token()
        media = Media()
        mid = media.upload(accessToken, output_image, 'image')

    except Exception as e:
        raise(e)
    finally:
        if os.path.exists(output_image):
            os.remove(output_image)
        if os.path.exists(msgId):
            os.rmdir(msgId)

    return mid

def weixin_variation_image(msgId, mediaId, size='256x256'):
    mid = None
    try:
        os.mkdir(msgId)
        input_image = os.path.join(msgId, 'input.jpg')
        rgba_image = os.path.join(msgId, 'rgba.png')
        output_image = os.path.join(msgId, 'output.png')

        accessToken = g_token.get_access_token()
        media = Media()
        media.get(accessToken, mediaId, input_image)

        os.system(f'ffmpeg -hide_banner -i {input_image} -s {size} -pix_fmt rgba {rgba_image} > /dev/null')

        variation_image(output_image, rgba_image, size)
        mid = media.upload(accessToken, output_image, 'image')

    except Exception as e:
        raise(e)
    finally:
        if os.path.exists(input_image):
            os.remove(input_image)
        if os.path.exists(rgba_image):
            os.remove(rgba_image)
        if os.path.exists(output_image):
            os.remove(output_image)
        if os.path.exists(msgId):
            os.rmdir(msgId)

    return mid

def weixin_process_audio(msgId, mediaId):
    text = None
    try:
        os.mkdir(msgId)
        input_audio = os.path.join(msgId, 'input.amr')
        mp3_audio = os.path.join(msgId, 'input.mp3')

        accessToken = g_token.get_access_token()
        media = Media()
        media.get(accessToken, mediaId, input_audio)

        os.system(f'ffmpeg -hide_banner -i {input_audio} {mp3_audio} > /dev/null')

        text = speech(mp3_audio)

    except Exception as e:
        raise(e)

    finally:
        if os.path.exists(input_audio):
            os.remove(input_audio)
        if os.path.exists(mp3_audio):
            os.remove(mp3_audio)
        if os.path.exists(msgId):
            os.rmdir(msgId)

    return text
