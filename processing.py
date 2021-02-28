import json
from telebot import apihelper, types, TeleBot


with open('credentials_for_bot.json', 'r', encoding='utf-8') as bot_file:
    credentials_bot = json.load(bot_file)
bot = TeleBot(credentials_bot["telegram"]["api_token"], skip_pending=True)


def reasons_olx(message):
    list_reasons = ["OLX Шахрайство", "OLX Агенція в рубриці від приватних осіб"]
    markup = types.ReplyKeyboardMarkup(True)
    for i in list_reasons:
        data_button = types.KeyboardButton(text=i)
        markup.add(data_button)
    bot.send_message(message.chat.id, text="Вибери причину", reply_markup=markup)


def reasons_flatfy(message):
    list_reasons = ["FLATFY Шахрайство", "FLATFY Мій ексклюзив / я — власник"]
    markup = types.ReplyKeyboardMarkup(True)
    for i in list_reasons:
        data_button = types.KeyboardButton(text=i)
        markup.add(data_button)
    bot.send_message(message.chat.id, text="Вибери причину", reply_markup=markup)


def counter(message):
    numbers = [1, 5, 10, 15, 20, 30, 50]
    markup = types.ReplyKeyboardMarkup(True)
    for i in numbers:
        data_button = types.KeyboardButton(text=str(i) + " разів")
        markup.add(data_button)
    bot.send_message(message.chat.id, text="Кількість повторень бану", reply_markup=markup)