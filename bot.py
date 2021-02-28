# coding=utf-8
import time
import json
import os
import re
import requests
import datetime
import logging
import threading
from datetime import datetime, timedelta, date
from telebot import apihelper, types, TeleBot

from services import ban_flatfy, ban_olx
from processing import reasons_olx, reasons_flatfy, counter

url = ''
choice_reason = ''
mode = 0
count = 0
urls = {}

with open('credentials_for_bot.json', 'r', encoding='utf-8') as bot_file:
    credentials_bot = json.load(bot_file)
bot = TeleBot(credentials_bot["telegram"]["api_token"], skip_pending=True)

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)  # or whatever
handler = logging.FileHandler('logs/' + datetime.now().strftime('%Y-%m-%d') + '.log', 'a', 'utf-8')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(message)s'))  # or whatever
root_logger.addHandler(handler)


all_reasons = {"Спам": "spam",
               "Шахрайство": "fraud",
               "Агенція в рубриці від приватних осіб": "agency",
               "Мій ексклюзив / я — власник": "my_ad"}


@bot.message_handler(commands=['start'])
def start_message(message):
    os.system("TASKKILL /F /IM chromedriver.exe /T")
    bot.send_message(message.chat.id, 'Hi!')
    bot.send_message(message.chat.id, 'Input url for ban')


@bot.message_handler(commands=['status'])
def start_message(message):
    for key, value in urls.items():
        if value:
            bot.send_message(message.chat.id, f'{key}: {value}')


@bot.message_handler(commands=['stop_bmi'])
def stop_bot(message):
    bot.send_message(message.chat.id, 'Bye')
    bot.stop_polling()
    os.system("TASKKILL /F /IM chromedriver.exe /T")


@bot.message_handler(regexp=r"stop http.*")
def stop_url(message):
    global urls
    key = re.findall(".* (.*)", message.text)[0]
    if urls.get(key) and urls[key] == 1:
        urls[key] = 0
        bot.send_message(message.chat.id, f'Stopped sending {key}')


@bot.message_handler(regexp=r"(1|5|10|15|20|30|50)\sразів")
def handler_count(message):
    global count, urls, url
    count = int(re.findall(r"\d+", message.text)[0])
    bot.send_message(message.chat.id, text="ОК", reply_markup=types.ReplyKeyboardRemove(True))
    urls.update({url: 1})
    logging.info(f"Urls: {urls}")
    if count and mode == 1:
        olx = threading.Thread(target=launch_olx, args=(count, message, url, choice_reason,))
        olx.start()
    elif count and mode == 2:
        flatfy = threading.Thread(target=launch_flatfy, args=(count, message, url, choice_reason,))
        flatfy.start()


@bot.message_handler(regexp=r"OLX\s.*")
def handler(message):
    global choice_reason
    choice_reason = all_reasons[re.findall("OLX (.*)", message.text)[0]]
    counter(message)


@bot.message_handler(regexp=r"FLATFY\s.*")
def handler(message):
    global choice_reason
    choice_reason = all_reasons[re.findall("FLATFY (.*)", message.text)[0]]
    counter(message)


@bot.message_handler(regexp=r"http(s*)://((www\.olx)|flatfy).*")
def handle_station(message):
    global url, mode
    if message.text.startswith('https://www.olx.ua/'):
        mode = 1
        url = message.text
        reasons_olx(message)

    if message.text.startswith('https://flatfy.ua/'):
        mode = 2
        url = message.text
        reasons_flatfy(message)


def launch_olx(count, message, url, reason):
    global urls
    logging.info(f"Start -- Mode: OLX User: {message.from_user.username} Url: {url} Count: {count}")
    while count and urls[url] == 1:
        result = ban_olx(message, url, reason)
        if result == 1:
            count -= 1
        elif result == -1:
            urls[url] = 0
            bot.send_message(message.chat.id, f'BANNED for {url} !!!')
            bot.send_message(368246133, f'BANNED for {url} !!!')
        else:
            continue
    if urls[url] == 1:
        urls[url] = 0
        logging.info(f"Finish -- Mode: OLX User: {message.from_user.username} Url: {url}")
        bot.send_message(message.chat.id, f'Закінчив відправку для посилання: {url}')


def launch_flatfy(count, message, url, reason):
    global urls
    logging.info(f"Start -- Mode: Flatfy User: {message.from_user.username} Url: {url} Count: {count}")
    while count and urls[url] == 1:
        result = ban_flatfy(message, url, reason)
        if result:
            count -= 1
        else:
            continue
    if urls[url] == 1:
        urls[url] = 0
        logging.info(f"Finish -- Mode: Flatfy User: {message.from_user.username} Url: {url}")
        bot.send_message(message.chat.id, f'Закінчив відправку для посилання: {url}')


bot.polling(none_stop=True)
