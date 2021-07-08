# -*- coding: utf-8 -*-
"""
Author: Tishacy
"""
import os
import json
import argparse
from threading import Thread

from loguru import logger
from apscheduler.schedulers.blocking import BlockingScheduler

from hitcarder.base import task_flow
from hitcarder.message import msg_sender_mapper, PushPlusMessageSender
from hitcarder.logger import log_init


def main():
    parser = argparse.ArgumentParser("Command line tool to run Hitcard tasks.")
    parser.add_argument('-c', '--config', help="config file path")
    args = parser.parse_args()

    if args.config:
        conf_fpath = args.config
    else:
        conf_dir = os.path.dirname(os.path.abspath(__file__))
        conf_fpath = os.path.join(conf_dir, 'config.json')

    # Load configs.
    log_init(conf_fpath)
    if not os.path.exists(conf_fpath):
        logger.error("No config file is found.")
        return
    configs = json.loads(open(conf_fpath, 'r').read())
    if 'tasks' not in configs:
        logger.error("No tasks found in the config file.")
        return
    logger.info("Load config file: %s." % conf_fpath)

    scheduler = BlockingScheduler()
    tasks = configs['tasks']
    for task in tasks:
        username, password, schedule = task.get('username'), task.get('password'), task.get('schedule')
        if not username or not password or not schedule:
            logger.warning("Not a valid task. A valid task must include keys: 'username', 'password' and 'schedule'.")
            continue
        hour, minute, rand_delay = schedule.get('hour'), schedule.get('minute'), schedule.get('rand_delay', 1200)
        if not hour or not minute:
            logger.warning("Not a valid task schedule. A valid task schedule must include keys: 'hour' and 'minute'.")
            continue

        # Send notification messages.
        msg_senders_config = task.get('msg_senders')
        msg_senders = []
        if msg_senders_config is not None and isinstance(msg_senders_config, list):
            for config in msg_senders_config:
                msg_sender_cls = msg_sender_mapper.get(config.get('type', 'wechat'), PushPlusMessageSender)
                msg_sender_init_args = config.get('init_args', {})
                msg_sender = msg_sender_cls(**msg_sender_init_args)
                msg_senders.append(msg_sender)

        # Register the task job.
        scheduler.add_job(task_flow, 'cron', args=(username, password, rand_delay, msg_senders), hour=hour, minute=minute)
        logger.info("Register task [%s - %02d:%02d - delay(0-%d)s]." % (username, hour, minute, rand_delay))

        if task.get('run_immediate', False):
            logger.info("Run task immediately for %s." % username)
            once_task = Thread(target=task_flow, args=(username, password, rand_delay, msg_senders))
            once_task.start()
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass


if __name__ == '__main__':
    main()
