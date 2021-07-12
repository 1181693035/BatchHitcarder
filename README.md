# ZJU-BatchHitcarder

 [![Pyversion](https://img.shields.io/badge/python-3.x-g)](https://pypi.org/project/qspider/) [![License: MIT](https://img.shields.io/badge/License-MIT-orange)](https://opensource.org/licenses/MIT)

 :sparkles:浙大健康打卡定时自动打卡脚本，简单易用

默认每次提交上次所提交的内容（只有时间部分更新）。系统表单如有更新，在当天自行手机打卡，后面会自动按照你更新后的选项继续打卡。

支持以下功能：

- 可定时，默认为每天6点5分

- 可随机延迟运行任意时间，默认随机延迟 [0~1200] 秒

- 可以配置多人打卡任务

- 可以配置打卡消息通知，目前支持：

  - wechat：需要在 [PushPlus](https://pushplus.hxtrip.com/) 上申请 token
  - mail：需要开启对应邮箱的 SMTP 服务

  > 每项打卡任务可以配置多个消息通知。

- 支持 log 日志，方便调试

项目用于学习交流，仅用于各项无异常时打卡，如有身体不适等情况还请自行如实打卡~

## Installation

使用 pip 安装即可

```bash
$ pip install zju_hitcarder
```

查看是否安装成功

```bash
$ hitcarder --help
Usage: hitcarder [OPTIONS] COMMAND [ARGS]...
  Command line tool to run ZJU Hitcard tasks.

Options:
  -v, --version  Show version information.
  -h, --help     Show this message and exit.

Commands:
  gen_config  Generate the config file.
  run         Run ZJU Hitcard tasks with the given configs.

$ hitcarder --version
1.0.0
```

## Usage

1. 首先，需要生成打卡配置文件。

   ```bash
   $ hitcarder gen_config ./myconfig.json
   [Info] Config file is generated: /Some/path/to/project/myconfig.json
   [Info] Now you could open your favourite text editor, and **modify your configs**!
   ```

   执行上述命令，会在当前目录下生成一个`myconfig.json` 的配置文件（你可以指定任何文件路径来生成此配置文件）。

2. 打开配置文件，修改所需要的配置项，并保存。

   ```bash
   $ vim myconfig.json
   {
       # "tasks" 是一个任务列表，可以给多个人配置多项任务。
       "tasks": [{
           # 这里填写你的浙大用户信息。
           "username": "<你的浙大统一认证平台用户名>",
           "password": "<你的浙大统一认证平台密码>",
           # 这里填写打卡日程时间，默认是每天上午 6:05，随机延迟 0~1200 秒。
           # 如不需要延迟，将 "rand_delay" 设为 0 即可。
           "schedule": {
               "hour": 6,
               "minute": 5,
               "rand_delay": 1200
           },
           # 这里配置当 hitcarder 进程启动时，是否需要立即执行一次本任务。
           "run_immediate": true,
           # 这里配置本项打卡任务的消息通知列表，当前支持 "wechat" 和 "mail" 两种类型。
           # 每项任务可以配置多个通知，如果不需要消息通知，将 "msg_senders" 设为空列表 [] 即可
           "msg_senders": [{
               "type": "wechat",
               "init_args": {
                   "token": "<你的 PushPlus token>"
               }
           },{
               "type": "mail",
               "init_args": {
                   "host_server": "<你的 SMTP server>",
                   "password": "<你的 SMTP 服务密码>",
                   "sender": "<发件人邮箱>",
                   "receiver": "<收件人邮箱>"
               }
           }]
       }],
       # 这里配置 log 信息。
       # "log_fpath" 可以是相对路径，也可以是绝对路径，
       # 日志所在目录可以不存在，hitcarder 会自动创建不存在的目录。
       "log": {
           "log_fpath": "./log/default.log",
           "rotation": "16MB",
           "encoding": "utf-8",
           "retention": "10 days"
       }
   }
   ```

   > 注意：修改完配置后尽量检查一下 json 格式是否有误，否则 hitcarder 解析配置文件会报 `json.decoder.JSONDecodeError` 错误。

3. 启动执行 Hitcarder!

   ```bash
   $ hitcarder run -c ./myconfig.json
   ```

   如果看到类似以下 log 信息，则启动成功。

   ```bash
   2021-07-12 16:43:11.233 | INFO     | hitcarder.cli:run:69 - Load config file: /Some/path/to/project/test_config.json.
   2021-07-12 16:43:11.238 | INFO     | hitcarder.logger:log_init:30 - Logging initialized: /Some/path/to/project/log/default.log
   2021-07-12 16:43:11.289 | INFO     | hitcarder.cli:run:103 - Register task [XXXXXXXX - 06:05 - delay(0-1200)s].
   2021-07-12 16:43:11.290 | INFO     | hitcarder.cli:run:106 - Run task immediately for XXXXXXXX.
   2021-07-12 16:43:11.290 | INFO     | hitcarder.base:__init__:40 - [Hitcarder-XXXXXXXX] HitCarder instance is created.
   2021-07-12 16:43:11.291 | INFO     | hitcarder.base:task_flow:191 - [Hitcarder-XXXXXXXX] Task will be delayed 3 seconds.
   2021-07-12 16:43:15.195 | INFO     | hitcarder.base:login:70 - [Hitcarder-XXXXXXXX] Successfully logined.
   2021-07-12 16:43:15.413 | INFO     | hitcarder.base:get_info:117 - [Hitcarder-XXXXXXXX] Successfully get submit info.
   2021-07-12 16:43:15.617 | INFO     | hitcarder.base:submit:135 - [Hitcarder-XXXXXXXX-XXX] Successfully hit card.
   2021-07-12 16:43:16.213 | INFO     | hitcarder.base:send_msgs:161 - [Hitcarder-XXXXXXXX-XXX] <PushPlusMessageSender> send a hit card message to you, hit card status: COMPLETE
   ```

## Deploy

- Linux：可以使用 nohup、systemd 等方式将程序在后台运行。
- Mac：可以使用 nohup 将程序后台执行。
- Windows：可以使用 sc、nssm 等方式将程序注册服务运行。

## LICENSE

Copyright (c) 2021 tishacy.

Licensed under the [MIT License](https://github.com/Tishacy/BatchHitcarder/blob/master/LICENSE)

