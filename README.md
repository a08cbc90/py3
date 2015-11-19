# py3
python3 test text

## Base
base function set

## conf
configuration files

## K2
knnnrhk-2nd

### log rotate
/etc/logrotate.d/git_k2_log setting example


    /home/user/anyware/log/*.log {
        weekly
        missingok
        rotate 99
        compress
        notifempty
        delaycompress
    }

### cron
crontab -e example
    0 8 * * * /home/user/anyware/script.py >/dev/null 2>/dev/null
