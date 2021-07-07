# -*- coding: utf-8 -*-
"""Message senders
Author: Tishacy
"""
import json
from abc import ABC, abstractmethod

import requests
from loguru import logger


class BaseMessageSender(ABC):
    """Base message sender."""
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def send(self, data):
        pass

    @abstractmethod
    def close(self):
        pass


class PushPlusMessageSender(BaseMessageSender):
    """Push Plus message sender.
    """
    push_plus_url = 'http://pushplus.hxtrip.com/send'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = kwargs.get("token")
        if self.token is None:
            raise ValueError("Push Plus token is not found.")
        self.template = kwargs.get("template", "html")
        self._sess = self._init_sess()

    @staticmethod
    def _init_sess():
        sess = requests.Session()
        sess.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"
        })
        return sess

    def send(self, data):
        if not isinstance(data, dict):
            raise ValueError("data must be a dict, got a %s type." % type(data))

        title = data.get('title', '')[:100]
        content = data.get('content', '')
        send_data = {
            "token": self.token,
            "title": title,
            "content": content,
            "template": self.template
        }
        res = self._sess.post(self.push_plus_url, data=json.dumps(send_data)).json()
        if res["code"] == 200:
            logger.info("Send the push plus message.")
            return True
        logger.warning("Failed to send the push plus message: %s" % send_data)
        return False

    def close(self):
        self._sess.close()

    def __repr__(self):
        return "<PushPlusMessageSender>"


msg_sender_mapper = {
    'wechat': PushPlusMessageSender
}
