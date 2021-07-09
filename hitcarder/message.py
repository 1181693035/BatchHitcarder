# -*- coding: utf-8 -*-
"""Message senders
Author: Tishacy
"""
import json
from abc import ABC, abstractmethod
from email.mime.text import MIMEText
from email.header import Header
from smtplib import SMTP_SSL

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
            return True
        return False

    def close(self):
        self._sess.close()

    def __repr__(self):
        return "<PushPlusMessageSender>"


class MailMessageSender(BaseMessageSender):
    """Mail message sender"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.host_server = kwargs.get("host_server")
        self.password = kwargs.get("password")
        self.sender = kwargs.get("sender")
        self.receiver = kwargs.get("receiver")
        self.template = kwargs.get("template", "html")
        self._smtp = None

    def _init_smtp(self):
        username = self.sender.split("@")[0] if 'qq' in self.sender else self.sender
        smtp = SMTP_SSL(self.host_server)
        smtp.set_debuglevel(1)
        smtp.ehlo(self.host_server)
        smtp.login(username, self.password)
        return smtp

    def send(self, data):
        if not isinstance(data, dict):
            raise ValueError("data must be a dict, got a %s type." % type(data))

        title = data.get('title', '')[:100]
        content = data.get('content', '')
        email = MIMEText(content, self.template, 'utf-8')
        email["Subject"] = Header(title, 'utf-8')
        email["From"] = self.sender
        email["To"] = self.receiver

        self._smtp = self._init_smtp()
        res = self._smtp.sendmail(self.sender, self.receiver, email.as_string())
        self._smtp.quit()
        if len(res.keys()) == 0:
            return True
        return False

    def close(self):
        if self._smtp is not None:
            self._smtp.quit()

    def __repr__(self):
        return "<MailMessageSender>"


msg_sender_mapper = {
    'wechat': PushPlusMessageSender,
    'mail': MailMessageSender
}
