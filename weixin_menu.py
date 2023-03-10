#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# filename: weixin_menu.py

import logging
import requests

from weixin_token import Token

logger = logging.getLogger('abc')

class Menu(object):
    def __init__(self):
        pass

    def create(self, postData, accessToken):
        url= f"https://api.weixin.qq.com/cgi-bin/menu/create?access_token={accessToken}"
        postData = postData.encode('utf-8')
        response = requests.post(url, data=postData)
        logger.debug(response.json())

    def query(self, accessToken):
        url = f"https://api.weixin.qq.com/cgi-bin/menu/get?access_token={accessToken}"
        response = requests.get(url)
        logger.debug(response.__dict__)

    def delete(self, accessToken):
        url = f"https://api.weixin.qq.com/cgi-bin/menu/delete?access_token={accessToken}"
        response = requests.get(url)
        logger.debug(response.__dict__)

    # 获取自定义菜单配置接口
    def get_current_selfmenu_info(self, accessToken):
        url = f"https://api.weixin.qq.com/cgi-bin/get_current_selfmenu_info?access_token={accessToken}"
        response = requests.get(url)
        logger.debug(response.__dict__)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    myMenu = Menu()
    postJson = """
    {
        "button":
        [
            {
                "type": "click",
                "name": "开发指引",
                "key":  "mpGuide"
            },
            {
                "name": "公众平台",
                "sub_button":
                [
                    {
                        "type": "view",
                        "name": "更新公告",
                        "url": "http://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1418702138&token=&lang=zh_CN"
                    },
                    {
                        "type": "view",
                        "name": "接口权限说明",
                        "url": "http://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1418702138&token=&lang=zh_CN"
                    },
                    {
                        "type": "view",
                        "name": "返回码说明",
                        "url": "http://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1433747234&token=&lang=zh_CN"
                    }
                ]
            },
            {
                "type": "media_id",
                "name": "旅行",
                "media_id": "z2zOokJvlzCXXNhSjF46gdx6rSghwX2xOD5GUV9nbX4"
            }
          ]
    }
    """
    accessToken = Token().get_access_token()
    logger.debug(accessToken)
    #myMenu.delete(accessToken)
    myMenu.create(postJson, accessToken)
