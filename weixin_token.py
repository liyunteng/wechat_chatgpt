# -*- coding: utf-8 -*-

import json
import time
import requests

import config

class Token:
    def __init__(self):
        self.__accessToken = ''
        self.__leftTime = 0

    def __real_get_access_token(self):
        url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={config.appId}&secret={config.appSecret}"
        response = requests.get(url)

        if 'access_token' not in response.json():
            raise(Exception(response.json()['errmsg']))

        self.__accessToken = response.json()['access_token']
        self.__leftTime = response.json()['expires_in']

    def get_access_token(self):
        if self.__leftTime < 10:
            self.__real_get_access_token()
        return self.__accessToken

    def run(self):
        while (True):
            if self.__leftTime > 10:
                time.sleep(2)
                self.__leftTime -= 2
            else:
                self.__real_get_access_token()
