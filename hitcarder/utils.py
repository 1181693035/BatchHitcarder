# -*- coding: utf-8 -*-
"""Utils used in HitCarder.
Author: Tishacy
"""


def rsa_encrypt(s, e_str, m_str):
    """Encrypt a string with RSA."""
    s_bytes = bytes(s, 'ascii')
    s_int = int.from_bytes(s_bytes, 'big')
    e_int = int(e_str, 16)
    m_int = int(m_str, 16)
    result_int = pow(s_int, e_int, m_int)
    return hex(result_int)[2:].rjust(128, '0')
