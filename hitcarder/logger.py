# -*- coding: utf-8 -*-
"""
Author: Tishacy
"""
import os
import json

from loguru import logger


def log_init(conf_fpath=None):
    """Initializing logger settings."""
    package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    conf_fpath = conf_fpath or os.path.join(package_dir, 'config.json')
    if not os.path.exists(conf_fpath):
        logger.error("Cannot find the config file %s." % conf_fpath)
        return False
    configs = json.loads(open(conf_fpath, 'r').read())

    log_config = configs.get('log', {})
    log_fpath = os.path.abspath(log_config.get('log_fpath', "./log/default.log"))
    log_dir = os.path.dirname(log_fpath)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    logger.add(log_fpath,
               rotation=log_config.get('rotation'),
               encoding=log_config.get('encoding'),
               enqueue=True,
               retention=log_config.get('retention'))
    logger.info("Logging initialized: %s" % log_fpath)
    return True
