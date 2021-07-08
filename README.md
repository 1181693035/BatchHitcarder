# ZJU-BatchHitcarder

# Installation
```bash
$ git clone https://github.com/Tishacy/BatchHitcarder.git
$ cd BatchHitcarder && python setup.py install
```

# Usage
```bash
# Generate config file.
$ hitcarder -g myconfig.json

# Modify the config file.
$ vim myconfig.json
{
    "tasks": [{
        # Specify your ZJU login information. 
        "username": "<你的浙大统一认证平台用户名>",
        "password": "<你的浙大统一认证平台密码>",
        "schedule": {
            "hour": 6,
            "minute": 5,
            "rand_delay": 4
        },
        # Whether to run the task immediately after the hitcarder starts.
        "run_immediate": true,
        # You could specify multiple message senders (notifications) for each task.
        # msg_sender type could be 'wechat' or 'mail' by now.
        # If you don't want any notifications, just let "msg_senders" be an empty list.
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
    # You could specify where to put logs and other logging configs.
    "log": {
        "log_fpath": "./log/default.log",
        "rotation": "16MB",
        "encoding": "utf-8",
        "retention": "10 days"
    }
}

# Run the hitcarder program.
$ hitcarder -c myconfig.json
```

You could use `nohup` or `systemd` to run the program in daemon.

