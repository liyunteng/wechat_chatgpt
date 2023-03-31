#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# main.py - main

# All rights reserved.

from gevent import monkey
monkey.patch_all()

import os
import sys
import time
import hashlib
import logging

from gevent.pywsgi import WSGIServer
from subprocess import Popen, PIPE
from flask import Flask, jsonify, request, abort, Response

import config
import weixin_reply
import weixin_receive
from weixin_tool import weixin_chatgpt, weixin_gen_image, weixin_variation_image, Cache, init_logging

logger = init_logging(debug=config.debug)
app = Flask(__name__)
g_cache = Cache()

def handle_gen_image(recvMsg):
    logger.info('GEN_IMAGE UserName: {} MsgId: {}'.format(recvMsg.FromUserName, recvMsg.MsgId))
    logger.debug('GEN_IMAGE: {}'.format(recvMsg.Content))
    mid = None

    if not g_cache.has(recvMsg):
        g_cache.put(recvMsg)
        req = recvMsg.Content[1:].strip()
        try:
            mid = weixin_gen_image(recvMsg.MsgId, req)
            g_cache.put(recvMsg, mid)
        except Exception as e:
            g_cache.put(recvMsg, mid, e)

    else:
        mid = g_cache.get(recvMsg)

    logger.debug('GEN_IMAGE Result: {}'.format(mid))
    return mid

def handle_chatgpt(recvMsg):
    logger.debug('Question: {}'.format(recvMsg.Content))
    answer = None

    if not g_cache.has(recvMsg):
        g_cache.put(recvMsg)
        try:
            answer = weixin_chatgpt(recvMsg.FromUserName, recvMsg.Content.strip())
            g_cache.put(recvMsg, answer)
        except Exception as e:
            g_cache.put(recvMsg, answer, e)
    else:
        answer = g_cache.get(recvMsg)

    logger.debug('Answer: {}'.format(answer))
    return answer

def handle_image(recvMsg):
    mid = None

    if not g_cache.has(recvMsg):
        g_cache.put(recvMsg)
        try:
            mid = weixin_variation_image(recvMsg.MsgId, recvMsg.MediaId)
            g_cache.put(recvMsg, mid)
        except Exception as e:
            g_cache.put(recvMsg, mid, e)
    else:
        mid = g_cache.get(recvMsg)

    return mid

def handle_voice(recvMsg):
    answer = None
    text = recvMsg.Recognition
    logger.debug('Question: {}'.format(text))

    if text is not None:
        if not g_cache.has(recvMsg):
            g_cache.put(recvMsg)
            try:
                answer = weixin_chatgpt(recvMsg.FromUserName, text)
                g_cache.put(recvMsg, answer)
            except Exception as e:
                g_cache.put(recvMsg, answer, e)
        else:
            answer = g_cache.get(recvMsg)
    else:
        answer = '请再说一遍，我没有听懂'

    logger.debug('Answer: {}'.format(answer))
    return answer

import json
from openai_test import chatgpt_generate_v2
@app.route('/web_v2', methods=['OPTIONS'])
def web_v2_options():
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': '*',
        'Access-Control-Allow-Headers': '*',
    }
    reply = Response(headers=headers)
    return reply

@app.route('/web_v2', methods=['POST'])
def web_v2():
    req = request.get_json()
    logger.debug('{}'.format(req))

    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': '*',
        'Access-Control-Allow-Headers': '*',
    }

    context = None
    prompt = None
    if 'context' in req:
        context = req['context']
    if 'prompt' in req:
        prompt = req['prompt']

    if prompt is None:
        abort(404)

    try:
        response = chatgpt_generate_v2(prompt, context)
        def generate_v2(response):
            for x in response.iter_lines(delimiter=b'\n\n'):
                if x == b'data: [DONE]':
                    return

                if len(x) < 20:
                    continue

                d = json.loads(x[6:])
                if 'content' in d['choices'][0]['delta']:
                    data = d['choices'][0]['delta']['content']
                    yield data
        reply = Response(generate_v2(response), headers=headers)
        return reply
    except Exception as e:
        def generate_error(ex):
            for x in "Exception: {}".format(ex):
                data = x
                yield data
        reply = Response(generate_error(e), headers=headers)
        return reply

from openai_function import chatgpt_generate
@app.route('/web', methods=['OPTIONS'])
def web_options():
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': '*',
        'Access-Control-Allow-Headers': '*',
    }
    reply = Response(headers=headers)
    return reply

@app.route('/web', methods=['POST'])
def web():
    req = request.get_json()
    logger.debug('{}'.format(req))

    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': '*',
        'Access-Control-Allow-Headers': '*',
    }

    context = None
    prompt = None
    if 'context' in req:
        context = req['context']
    if 'prompt' in req:
        prompt = req['prompt']

    if prompt is None:
        abort(404)

    try:
        response = chatgpt_generate(prompt, context, timeout=(10, 30))
        def generate(response):
            for x in response:
                if 'content' in x['choices'][0]['delta']:
                    data = x['choices'][0]['delta']['content']
                    yield data
        reply = Response(generate(response), headers=headers)
        return reply
    except Exception as e:
        def generate_error(ex):
            for x in "Exception: {}".format(ex):
                data = x
                yield data
        reply = Response(generate_error(e), headers=headers)
        return reply

@app.route('/wx', methods=['GET'])
def auth():
    logger.debug('\n{}'.format(request.args.decode('utf-8')))

    signature = str(request.args.get('signature'))
    timestamp = str(request.args.get('timestamp'))
    nonce = str(request.args.get('nonce'))
    echostr = str(request.args.get('echostr'))

    l = [config.token, timestamp, nonce]
    l.sort()
    sha1 = hashlib.sha1()
    for x in l:
        sha1.update(x.encode('utf-8'))
    hashcode = sha1.hexdigest()
    if hashcode == signature:
        logger.info('auth success')
        return echostr
    else:
        logger.error("auth failed")
        return ""

@app.route('/wx', methods=['POST'])
def message():
    logger.debug('\n{}'.format(request.data.decode('utf-8')))

    try:
        start = time.time()
        replyMsg = None
        recvMsg = weixin_receive.parse_xml(request.data)
        fromUserName = recvMsg.FromUserName
        toUserName = recvMsg.ToUserName
        if isinstance(recvMsg, weixin_receive.Msg):
            logger.info('{} UserName: {} MsgId: {}'.format(recvMsg.MsgType, recvMsg.FromUserName, recvMsg.MsgId))
            if recvMsg.MsgType == 'text':
                if recvMsg.Content.startswith('@') or recvMsg.Content.startswith('画 '):
                    mid = handle_gen_image(recvMsg)
                    if mid is not None:
                        replyMsg = weixin_reply.ImageMsg(recvMsg.FromUserName, recvMsg.ToUserName, mid)

                else:
                    answer = handle_chatgpt(recvMsg)
                    if answer is not None:
                        replyMsg = weixin_reply.TextMsg(recvMsg.FromUserName, recvMsg.ToUserName, answer)

            elif recvMsg.MsgType == 'image':
                mid = handle_image(recvMsg)
                if mid is not None:
                    replyMsg = weixin_reply.ImageMsg(recvMsg.FromUserName, recvMsg.ToUserName, mid)

            elif recvMsg.MsgType == 'voice':
                answer = handle_voice(recvMsg)
                if answer is not None:
                    replyMsg = weixin_reply.TextMsg(recvMsg.FromUserName, recvMsg.ToUserName, answer)

            elif recvMsg.MsgType == 'location':
                replyMsg = weixin_reply.LocationMsg(recvMsg.FromUserName, recvMsg.ToUserName,
                                             recvMsg.Location_X, recvMsg.Location_Y,
                                             recvMsg.Scale, recvMsg.Label)
            elif recvMsg.MsgType == 'file':
                replyMsg = weixin_reply.FileMsg(recvMsg.FromUserName, recvMsg.ToUserName,
                                         recvMsg.Title, recvMsg.Description,
                                         recvMsg.FileKey, recvMsg.FileMd5,
                                         recvMsg.FileTotalLen)

        elif isinstance(recvMsg, weixin_receive.EventMsg):
            logger.info('Event {} UserName: {}'.format(recvMsg.Event, recvMsg.FromUserName))
            if recvMsg.Event == 'CLICK':
                if recvMsg.Eventkey == 'mpGuid':
                    answer = 'mpGuid'.encode('utf-8')
                    replyMsg = weixin_reply.TextMsg(fromUserName, toUserName, answer)
            elif recvMsg.Event == 'subscribe':
                answer ='这是一个基于ChatGPT的聊天公众号'
                replyMsg = weixin_reply.TextMsg(fromUserName, toUserName, answer)
            elif recvMsg.Event == 'unsubscribe':
                pass

        if replyMsg is not None:
            logger.info('spand: {}'.format(time.time() - start))
            return replyMsg.send()
        else:
            logger.info('spand: {}'.format(time.time() - start))
            return 'success'

    except Exception as e:
        logger.error(e)
        replyMsg = weixin_reply.TextMsg(fromUserName, toUserName, 'Exception: {}'.format(e))
        return replyMsg.send()


def main():
    server = WSGIServer(('0.0.0.0', 80), app)
    server.serve_forever()

if __name__ == '__main__':
    main()
