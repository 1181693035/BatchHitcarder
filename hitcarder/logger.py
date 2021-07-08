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
        logger.error("No config file is found.")
        return
    configs = json.loads(open(conf_fpath, 'r').read())

    log_config = configs.get('log', {})
    logger.add(os.path.join(package_dir, "log", log_config.get('logfile_name', "default.log")),
               rotation=log_config.get('rotation'),
               encoding=log_config.get('encoding'),
               enqueue=True,
               retention=log_config.get('retention'))
    logger.info("Logging initialized.")
