#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# filename: weixin_material.py

import json
import logging
import requests

from weixin_token import Token

logger = logging.getLogger('abc')

class Material(object):
    def upload(self, accessToken, filePath, fileName, mediaType):
        url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={accessToken}&type={mediaType}"

        with open(filePath, 'rb') as fp:
            files = {'media': fp, 'filename': fileName}
            response = requests.post(url, files=files)
            logger.debug(response.json())
            media_id = response.json()['media_id']
            return media_id

    def get(self, accessToken, mediaId, filePath):
        url = f"https://api.weixin.qq.com/cgi-bin/material/get_material?access_token={accessToken}"
        params = {'media_id': mediaId}

        response = requests.post(url, json=params)
        headers = response.__dict__['headers']
        logger.debug(headers)
        if 'Content-Type: application/json\r\n' in headers or 'Content-Type: text/plain\r\n' in headers:
            data = response.json()
            logger.debug(data)
        else:
            with open(filePath, 'wb') as f:
                f.write(response.content)

    def delete(self, accessToken, mediaId):
        url = f"https://api.weixin.qq.com/cgi-bin/material/del_material?access_token={accessToken}"
        params =  {'media_id': mediaId}

        response = requests.post(url, json=params)
        logger.debug(response.json())

    def batch_get(self, accessToken, mediaType, offset=0, count=20):
        url = f"https://api.weixin.qq.com/cgi-bin/material/batchget_material?access_token={accessToken}"
        params = {'type': mediaType, 'offset': offset, 'count': count}

        response = requests.post(url, json=params)
        logger.debug(response.json())


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    accessToken = Token().get_access_token()
    m = Material()

    filePath = 'test.jpg'
    fileName = 'hello.jpg'
    mediaType = 'image'
    mediaId = m.upload(accessToken, filePath, fileName, mediaType)

    m.get(accessToken, mediaId, 'material_get.jpg')

    # m.batch_get(accessToken, mediaType)
    # m.delete(accessToken, mediaId)
