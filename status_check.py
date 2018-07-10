import os
import sys
import time
import requests
import logging
from requests_html import HTMLSession

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
URL = 'https://egov.uscis.gov/casestatus/mycasestatus.do'
USER_AGENT = '"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"'
HEADER = {'user-agent': USER_AGENT}
XPATH_STATUS = '/html/body/div[2]/form/div/div[1]/div/div/div[2]/div[3]/h1'
XPATH_DESCRIPTION = '/html/body/div[2]/form/div/div[1]/div/div/div[2]/div[3]/p'
TELEGRAM_API = 'https://api.telegram.org/bot{}/{}?chat_id={}&text={}'


def check_status(id):
    payload = {'initCaseSearch': 'CHECK STATUS', 'appReceiptNum': id}
    with HTMLSession() as s:
        r = s.post(URL, headers=HEADER, data=payload)
        status = r.html.xpath(XPATH_STATUS, first=True).full_text
        info = r.html.xpath(XPATH_DESCRIPTION, first=True).full_text
    return status, info


def send_notification(telegram_bot_api, telegram_id, content):
    r = requests.get(
        TELEGRAM_API.format(
            telegram_bot_api,
            'sendMessage',
            telegram_id,
            content))
    if r.status_code != 200:
        logging.error(
            'Message failed to be sent to chat {}'.format(telegram_id))


def check_periodically(id, telegram_bot_api, telegram_id):
    records = []
    with open('status_log', 'a+') as f:
        for line in f:
            status, info = line.split(': ')
            records.append(status)
        while True:
            status, info = check_status(id)
            if not records:
                logging.info('First status check completed')
                content = 'Current Status:\n{}\n{}'.format(status, info)
                send_notification(telegram_bot_api, telegram_id, content)
                records.append(status)
                f.write("{}: {}".format(status, info))
                f.flush()
            elif status != records[-1]:
                logging.info('New Status found: {}'.format(status))
                content = 'New Status Found:\n{}\n{}'.format(status, info)
                send_notification(telegram_bot_api, telegram_id, content)
                records.append(status)
                f.write("{}: {}".format(status, info))
                f.flush()
            else:
                logging.info('Status has not been changed')
            try:
                time.sleep(12 * 60 * 60)
            except KeyboardInterrupt:
                logging.info('Program exits on C-c')
                sys.exit(0)


if __name__ == '__main__':
    case_id = os.getenv('USCIS_CASE_ID')
    telegram_bot_api = os.getenv('TELEGRAM_BOT_API')
    telegram_id = os.getenv('TELEGRAM_ID')
    if not case_id:
        logging.critical("No environment variable USCIS_CASE found!")
        sys.exit(1)
    if not telegram_bot_api:
        logging.critical("No environment variable TELEGRAM_API found!")
        sys.exit(1)
    if not telegram_id:
        logging.critical("No environment variable TELEGRAM_ID found!")
        sys.exit(1)
    check_periodically(case_id, telegram_bot_api, telegram_id)
