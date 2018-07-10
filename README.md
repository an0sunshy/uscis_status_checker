### Usage:

```bash
USCIS_CASE_ID='YOUR CASE ID' TELEGRAM_BOT_API='YOUR TELEGRAM BOT TOKEN' TELEGRAM_ID='YOUR CHAT_ID' python3 status_check.py
```

It is defaulted to repeatedly check status every 12 hours, and send a message to specified telegram chat once a different status has been found.

Docker version can be found: https://github.com/an0sunshy/dockerfiles/tree/master/uscis-status-checker