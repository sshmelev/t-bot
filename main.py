import telebot
bot = telebot.TeleBot('', parse_mode='MARKDOWN')

from telebot import types

import re
from datetime import datetime

import account_manager
import message_analyzer

import logging
logging.basicConfig(level=logging.INFO)

@bot.message_handler(commands=['start'])
def check_user_account(message):
    bot.send_message(message.from_user.id, message.from_user.first_name + ', '+ account_manager.Account(message.from_user.id).check())

@bot.message_handler(content_types=['text'])    
def main(message):

    # создание и отправка кравиатуры с наиболее частыми запросами на показ данных
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard = True)
    itembtn1 = types.KeyboardButton('Показать все')
    itembtn2 = types.KeyboardButton('Показать по категории')
    itembtn3 = types.KeyboardButton('Показать по дате')
    itembtn4 = types.KeyboardButton('Показать по аккаунтам')
    itembtn5 = types.KeyboardButton('Показать по категории и дате')
    itembtn6 = types.KeyboardButton('Показать по аккаунтам и категории')
    itembtn7 = types.KeyboardButton('Показать по аккаунтам и категории вместе')
    keyboard.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5, itembtn6, itembtn7)
    
    analyzed = message_analyzer.Analyzer().message_analyzer(message.text.lower())
    output_message = '\n'.join(analyzed[0])
    try: # может придти ValueError
        output_data = analyzed[1][0] 
    except:
        output_data= []
    output_code = analyzed[2]

    # если есть запрос на добавление, то добавляем
    if 'add' in output_code:
        logging.info('\n > now: ' + str(datetime.now()) + '\n > user: ' + str(message.from_user.id) + '\n > add: ' + str(output_data) + '\n > message: ' + message.text.lower() + '\n')
        bot.send_message(message.from_user.id, output_message + '\n\n' + account_manager.Account(message.from_user.id).add_expense(output_data), reply_markup = keyboard)
    # иначе, если есть запросы на получение данных выдаем результат и клавиатуру с запросами
    elif len(re.findall(r'get_', str(output_code))) > 0:
        logging.info('\n > now: ' + str(datetime.now()) + '\n > user: ' + str(message.from_user.id) + '\n > get: ' + str(output_code) + '\n > message: ' + message.text.lower() + '\n')
        bot.send_message(message.from_user.id, account_manager.Account(message.from_user.id).get_expense(output_code), reply_markup = keyboard)    
    # удаление последней добавленной записи    
    elif 'cancel' in output_code:
        logging.info('\n > now: ' + str(datetime.now()) + '\n > user: ' + str(message.from_user.id) + '\n > cancel: ' + str(output_code) + '\n > message: ' + message.text.lower() + '\n')
        bot.send_message(message.from_user.id, account_manager.Account(message.from_user.id).cancel_expense(), reply_markup = keyboard)         
    # очистка базы
    elif 'clear' in output_code:
        logging.info('\n > now: ' + str(datetime.now()) + '\n > user: ' + str(message.from_user.id) + '\n > clear: ' + str(output_code) + '\n > message: ' + message.text.lower() + '\n')
        bot.send_message(message.from_user.id, account_manager.Account(message.from_user.id).clear_expense(), reply_markup = keyboard)
    # создание или удаление связи аккаунтов
    elif len(re.findall(r'_link', str(output_code))) > 0:
        logging.info('\n > now: ' + str(datetime.now()) + '\n > user: ' + str(message.from_user.id) + '\n > link: ' + str(output_code) + '\n > message: ' + message.text.lower() + '\n')
        bot.send_message(message.from_user.id, account_manager.Account(message.from_user.id).account_link(output_data, output_code), reply_markup = keyboard)  
    else:
        logging.info('\n > now: ' + str(datetime.now()) + '\n > user: ' + str(message.from_user.id) + '\n > other: ' + str(output_code) + '\n > message: ' + message.text.lower() + '\n')
        bot.send_message(message.from_user.id, output_message, reply_markup = keyboard) 

if __name__ == '__main__':
	bot.polling(none_stop=True, interval=0)
