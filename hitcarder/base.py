# -*- coding: utf-8 -*-
"""HitCarder module.
Author: Tishacy
"""
import re
import json
import time
import random
import datetime
import traceback

import requests
from loguru import logger

from .utils import rsa_encrypt
from .exception import LoginError, RegexMatchError, DecodeError


class HitCarder(object):
    """Hit carder class

    :argument uname: (str) ZJU username, typically is student ID number.
    :argument passwd: (str) ZJU password.
    """
    _pub_key_url = "https://zjuam.zju.edu.cn/cas/v2/getPubKey"
    _login_url = "https://zjuam.zju.edu.cn/cas/login?service=https%3A%2F%2Fhealthreport.zju.edu.cn%2Fa_zju%2Fapi%2Fsso%2Findex%3Fredirect%3Dhttps%253A%252F%252Fhealthreport.zju.edu.cn%252Fncov%252Fwap%252Fdefault%252Findex"
    _base_url = "https://healthreport.zju.edu.cn/ncov/wap/default/index"
    _save_url = "https://healthreport.zju.edu.cn/ncov/wap/default/save"
    _sess_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"
    }

    def __init__(self, uname, passwd, msg_senders=None):
        self.username = uname
        self.password = passwd
        self.msg_senders = msg_senders or []
        self.sess = self._init_sess()
        self.info = {}
        self.status = "INITIALIZED"
        logger.info("%s HitCarder instance is created." % self)

    @staticmethod
    def _init_sess():
        sess = requests.Session()
        sess.headers.update(HitCarder._sess_headers)
        return sess

    def login(self):
        """Login to ZJU platform.
        :return An instance of requests.Session after login
        :raise LoginError
        """
        res = self.sess.get(self._login_url)
        execution = re.search('name="execution" value="(.*?)"', res.text).group(1)
        res = self.sess.get(url=self._pub_key_url).json()
        n, e = res['modulus'], res['exponent']
        encrypt_password = rsa_encrypt(self.password, e, n)
        data = {
            'username': self.username,
            'password': encrypt_password,
            'execution': execution,
            '_eventId': 'submit'
        }
        res = self.sess.post(url=self._login_url, data=data)

        # check if login successfully
        if '统一身份认证' in res.content.decode():
            self.status = "FAILED_LOGIN"
            raise LoginError('Login failed. Please check your ZJU username and password.')
        logger.info("%s Successfully logined." % self)
        self.status = "LOGINED"
        return self.sess

    def get_info(self, html=None):
        """Get hit card info, which is the old info with updated new time.
        :param html: Html string of base submit page.
        :return An hit card info dict.
        :raise RegexMatchError, if cannot find cache in html.
        :raise RegexMatchError, if cannot find specific info with regex.
        :raise DecodeError, if cannot decode the info string in html.
        """
        if not html:
            res = self.sess.get(self._base_url)
            html = res.content.decode()

        try:
            old_infos = re.findall(r'oldInfo: ({[^\n]+})', html)
            old_infos = old_infos if len(old_infos) != 0 else re.findall(r'def = ({[^\n]+})', html)
            if len(old_infos) != 0:
                old_info = json.loads(old_infos[0])
            else:
                self.status = "NO_CACHE"
                raise RegexMatchError("No cache info is found. Please manually hit card once before running this script.")

            new_info_tmp = json.loads(re.findall(r'def = ({[^\n]+})', html)[0])
            new_id = new_info_tmp['id']
            name = re.findall(r'realname: "([^\"]+)",', html)[0]
            number = re.findall(r"number: '([^\']+)',", html)[0]
        except IndexError as err:
            self.status = "NO_CACHE"
            raise RegexMatchError('No hit card info is found in html with regex: ' + str(err))
        except json.decoder.JSONDecodeError as err:
            self.status = "DECODE_ERROR"
            raise DecodeError('JSON decode error: ' + str(err))

        new_info = old_info.copy()
        new_info['id'] = new_id
        new_info['name'] = name
        new_info['number'] = number
        new_info["date"] = datetime.date.today().strftime("%Y%m%d")
        new_info["created"] = round(time.time())
        new_info['jrdqtlqk[]'] = 0
        new_info['jrdqjcqk[]'] = 0
        new_info['jcqzrq'] = ""
        new_info['gwszdd'] = ""
        new_info['szgjcs'] = ""
        logger.info("%s Successfully get submit info." % self)
        self.info = new_info
        self.status = "GOT_INFO"
        return new_info

    def submit(self, info=None):
        """Submit the hit card info.
        :return A boolean value of whether to submit hit card info successfully.
        """
        info = info or self.get_info()

        try:
            res = self.sess.post(self._save_url, data=info)
            res_json = json.loads(res.text)
            if str(res_json['e']) == '0':
                logger.info("%s Successfully hit card." % self)
                self.status = "COMPLETE"
                return True
            logger.info("%s Hit card info is already submitted today." % self)
            self.status = "ALREADY_COMPLETE"
            return True
        except Exception as e:
            logger.warning("%s Failed to submit the hit card info: %s." % (self, e))
            self.status = "FAILED_SUBMIT"
            return False

    def send_msgs(self, submit_success):
        """Send hit card messages.
        :param submit_success: (bool) Whether to hit card successfully.
        """
        data = {}
        if submit_success:
            data['title'] = '[%s 同学] 打卡成功！' % (self.info.get('name', self.username))
            data['content'] = '🦄 已为您打卡成功！</br>最终打卡状态: %s</br>打卡时间 %s' \
                              % (self.status, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        else:
            data['title'] = '[%s 同学] 打卡失败！' % (self.info.get('name', self.username))
            data['content'] = '❌ 打卡失败！请手动打卡~</br>最终打卡状态: %s</br>打卡时间 %s' \
                              % (self.status, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        for msg_sender in self.msg_senders:
            try:
                status = msg_sender.send(data)
                if status:
                    logger.info("%s %s send a hit card message to you, hit card status: %s"
                                % (self, msg_sender, self.status))
                else:
                    logger.warning("%s %s failed to send a hit card message to you, hit card status: %s"
                                   % (self, msg_sender, self.status))
            except Exception as e:
                logger.warning("%s %s failed to send a hit card message to you, hit card status: %s, Error msg: %s"
                               % (self, msg_sender, self.status, e))
                traceback.print_exc()

    def __repr__(self):
        if self.info.get('name'):
            return "[Hitcarder-%s-%s]" % (self.username, self.info.get('name'))
        return "[Hitcarder-%s]" % self.username


def task_flow(username, password, rand_delay=1200, msg_senders=None):
    """A hit card task flow.

    :param username: (str) ZJU username, typically is student ID number.
    :param password: (str) ZJU password.
    :param rand_delay: (int) Task will be randomly delayed for [0, rand_delay] seconds.
    :param msg_senders: (List[subclass of BaseMessageSender]) A list of message senders.
    """
    if msg_senders is None:
        msg_senders = []

    carder = HitCarder(username, password, msg_senders)

    # Random delay the task to mimic human behavior.
    sleep_time = random.randint(0, rand_delay)
    logger.info("%s Task will be delayed %d seconds." % (carder, sleep_time))
    time.sleep(sleep_time)

    # Login and hit card.
    is_success = False
    try:
        carder.login()
        is_success = carder.submit()
    except Exception as e:
        logger.warning("Task flow error: " + str(e))
        traceback.print_exc()
    carder.send_msgs(is_success)
    return is_success
