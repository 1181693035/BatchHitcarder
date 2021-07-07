# -*- coding: utf-8 -*-
"""Exceptions used in hitcarder.
Author: Tishacy
"""


class LoginError(Exception):
    """Login Exception"""
    pass


class RegexMatchError(Exception):
    """Regex Matching Exception"""
    pass


class DecodeError(Exception):
    """JSON Decode Exception"""
    pass
