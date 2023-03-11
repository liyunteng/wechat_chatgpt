#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# filename: weixin_media.py

import json
import logging
import requests

from weixin_token import Token

logger = logging.getLogger('abc')

class Media(object):
    def __init__(self):
        pass

    def upload(self, accessToken, filePath, mediaType):
        url = f"https://api.weixin.qq.com/cgi-bin/media/upload?access_token={accessToken}&type={mediaType}"

        with open(filePath, 'rb') as fp:
            files = {'media': fp}
            response = requests.post(url, files=files)
            if not response.ok:
                raise(Exception(f'{response.status_code}: {response.content}'))

            logger.debug(response.json())
            if 'media_id' not in response.json():
                raise(Exception(response.json()['errmsg']))

            media_id = response.json()['media_id']
            return media_id

    def get(self, accessToken, mediaId, filename):
        url = f"https://api.weixin.qq.com/cgi-bin/media/get?access_token={accessToken}&media_id={mediaId}"

        response = requests.get(url)
        if not response.ok:
            raise(Exception(f'{response.status_code}: {response.content}'))

        headers = response.__dict__['headers']
        logger.debug(headers)
        if 'Content-Type: application/json\r\n' in headers or 'Content-Type: text/plain\r\n' in headers:
            logger.debug(response.json())
        else:
            with open(filename, 'wb') as fp:
                fp.write(response.content)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    myMedia = Media()
    accessToken = Token().get_access_token()

    myMedia.get(accessToken, 'PLPbD8LkwR8_uKiM14lGNPDF7lbhB6Veyxh8La4vfYnLkdAuETT8NL9Frd9tTX3K', 'test_get.jpg')
    # filePath = 'test.jpg'
    # mediaType = 'image'
    # mediaId = myMedia.upload(accessToken, filePath, mediaType)

    # myMedia.get(accessToken, mediaId)
