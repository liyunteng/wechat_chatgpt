# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET

def parse_xml(web_data):
    if len(web_data) == 0:
        return None

    xmlData = ET.fromstring(web_data)
    msg_type = xmlData.find('MsgType').text
    if msg_type == 'event':
        event_type = xmlData.find('Event').text
        if event_type == 'CLICK':
            return Click(xmlData)
        elif event_type in ('subscribe', 'unsubscribe'):
            return Subscribe(xmlData)
        # elif event_type == 'VIEW':
        #     return View(xmlData)
        # elif event_type == 'LOCATION':
        #     return LocationEvent(xmlData)
        # elif event_type = 'SCAN':
        #     return Scan(xmlData)
    elif msg_type == 'text':
        return TextMsg(xmlData)
    elif msg_type == 'image':
        return ImageMsg(xmlData)
    elif msg_type == 'voice':
        return VoiceMsg(xmlData)
    elif msg_type == 'location':
        return LocationMsg(xmlData)
    elif msg_type == 'file':
        return FileMsg(xmlData)
    else:
        return Msg(xmlData)



class Msg(object):
    def __init__(self, xmlData):
        self.ToUserName = xmlData.find('ToUserName').text
        self.FromUserName = xmlData.find('FromUserName').text
        self.CreateTime = xmlData.find('CreateTime').text
        self.MsgType = xmlData.find('MsgType').text
        self.MsgId = xmlData.find('MsgId').text

class TextMsg(Msg):
    def __init__(self, xmlData):
        Msg.__init__(self, xmlData)
        self.Content = xmlData.find('Content').text

class ImageMsg(Msg):
    def __init__(self, xmlData):
        Msg.__init__(self, xmlData)
        self.PicUrl = xmlData.find('PicUrl').text
        self.MediaId = xmlData.find('MediaId').text

class VoiceMsg(Msg):
    def __init__(self, xmlData):
        Msg.__init__(self, xmlData)
        self.MediaId = xmlData.find('MediaId').text
        self.Format = xmlData.find('Format').text
        self.Recognition = xmlData.find('Recognition').text

class LocationMsg(Msg):
    def __init__(self, xmlData):
        Msg.__init__(self, xmlData)
        self.Location_X = xmlData.find('Location_X').text
        self.Location_Y = xmlData.find('Location_Y').text
        self.Scale = xmlData.find('Scale').text
        self.Label = xmlData.find('Label').text

class FileMsg(Msg):
    def __init__(self, xmlData):
        Msg.__init__(self, xmlData)
        self.Title = xmlData.find('Title').text
        self.Description = xmlData.find('Description').text
        self.FileKey = xmlData.find('FileKey').text
        self.FileMd5 = xmlData.find('FileMd5').text
        self.FileTotalLen = xmlData.find('FileTotalLen').text


class EventMsg(object):
    def __init__(self, xmlData):
        self.ToUserName = xmlData.find('ToUserName').text
        self.FromUserName = xmlData.find('FromUserName').text
        self.CreateTime = xmlData.find('CreateTime').text
        self.MsgType = xmlData.find('MsgType').text
        self.Event = xmlData.find('Event').text

class Click(EventMsg):
    def __init__(self, xmlData):
        EventMsg.__init__(self, xmlData)
        self.Eventkey = xmlData.find('EventKey').text

class Subscribe(EventMsg):
    def __init__(self, xmlData):
        EventMsg.__init__(self, xmlData)
        self.EventKey = xmlData.find('EventKey').text
        # self.Ticket = xmlData.find('Ticket').text
