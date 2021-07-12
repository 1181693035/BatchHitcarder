# -*- coding: utf-8 -*-
"""
Author: Tishacy
"""
import os
import json
import pkg_resources
from threading import Thread

import click
from loguru import logger
from apscheduler.schedulers.blocking import BlockingScheduler

from .base import task_flow
from .message import msg_sender_mapper, PushPlusMessageSender
from .logger import log_init


INFO = click.style("[Info] ", fg="green")
WARN = click.style("[Warn] ", fg="yellow")
ERROR = click.style("[Error] ", fg="red")

VERSION = pkg_resources.require("zju_hitcarder")[0].version


@click.group()
@click.version_option(VERSION, "-v", "--version", help="Show version information.")
@click.help_option("-h", "--help")
def cli():
    """Command line tool to run ZJU Hitcard tasks."""


@cli.command("gen_config")
@click.argument("CONFIG_FILE", default="./myconfig.json", required=False)
@click.option("-f", "--force", is_flag=True, help="Force to overwrite the existing config file.")
@click.help_option("-h", "--help")
def generate_config(config_file, force):
    """Generate the config file."""
    conf_fpath = os.path.abspath(config_file)
    if not os.path.exists(os.path.dirname(conf_fpath)):
        os.makedirs(os.path.dirname(conf_fpath))

    conf_template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'template')
    conf_template_fpath = os.path.join(conf_template_dir, 'config.json.templ')
    if not os.path.exists(conf_template_fpath):
        click.echo(ERROR + "No config template file is found.", )
        return

    if os.path.exists(conf_fpath) and not force:
        click.echo(WARN + "Config file %s already exists, use '-f' or '--force' to overwrite it." % conf_fpath)
        return

    with open(conf_fpath, 'w', encoding='utf-8') as f:
        f.write(open(conf_template_fpath, 'r', encoding='utf-8').read())
    click.echo(INFO + "Config file is generated: %s" % os.path.abspath(conf_fpath))
    click.echo(INFO + "Now you could open your favourite text editor, and "
               + click.style("modify your configs!", fg="yellow", bold=True))
    return


@cli.command("run")
@click.option("-c", "--config", default='./myconfig.json', help="Config file path. Default is ./myconfig.json")
@click.help_option("-h", "--help")
def run(config):
    """Run ZJU Hitcard tasks with the given configs."""

    # Load configs.
    conf_fpath = os.path.abspath(config)
    logger.info("Load config file: %s." % conf_fpath)
    if not log_init(conf_fpath):
        return

    configs = json.loads(open(conf_fpath, 'r', encoding='utf-8').read())
    if 'tasks' not in configs:
        logger.error("No tasks found in the config file.")
        return

    scheduler = BlockingScheduler()
    tasks = configs.get('tasks', [])
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
        scheduler.add_job(task_flow, 'cron', args=(username, password, rand_delay, msg_senders), hour=hour,
                          minute=minute)
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
    cli()
