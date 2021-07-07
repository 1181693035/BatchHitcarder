# -*- coding: utf-8 -*-
"""Test cases of Hit carder.
Author: Tishacy
"""
import os
import unittest

from loguru import logger


class TestMessageSender(unittest.TestCase):
    """Test case of message senders."""
    def test_push_plus(self):
        from .message import PushPlusMessageSender

        # An error case: Instantiate a push plus message sender with no token.
        with self.assertRaises(ValueError):
            PushPlusMessageSender()

        # NOTE: Recommend setting your push plus token to environment variable
        # PUSH_PLUS_TOKEN to test this case.
        token = os.environ.get('PUSH_PLUS_TOKEN')
        if token is None:
            with self.assertRaises(ValueError):
                PushPlusMessageSender(token=token)
        else:
            logger.info("Push Plus token: %s" % token)
            msg_sender = PushPlusMessageSender(token=token)
            self.assertTrue(msg_sender.send({
                'title': 'TEST: Success!',
                'content': '<h3>Successfully hit card!</h3>'
            }))
            msg_sender.close()


if __name__ == '__main__':
    unittest.main()
