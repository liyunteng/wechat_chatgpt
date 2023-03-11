# -*- coding: utf-8 -*-

import json
import time
import requests
import logging

import config

logger = logging.getLogger('abc')

class Token:
    def __init__(self):
        self.__accessToken = ''
        self.__expireTime = 0

    def __real_get_access_token(self):
        url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={config.appId}&secret={config.appSecret}"
        response = requests.get(url)

        if not response.ok:
            raise(Exception(f'{response.status_code}: {response.content}'))

        if 'access_token' not in response.json():
            raise(Exception(response.json()['errmsg']))

        self.__accessToken = response.json()['access_token']
        self.__expireTime = time.time() + response.json()['expires_in']
        logger.debug(f'accessToken update {self.__accessToken} {self.__expireTime}')

    def get_access_token(self):
        if self.__expireTime - time.time() < 10:
            self.__real_get_access_token()
        return self.__accessToken
