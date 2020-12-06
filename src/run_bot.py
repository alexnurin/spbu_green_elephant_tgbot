from threading import Thread
import telebot
import openpyxl as op
import logging
from time import sleep
from data.secret import token
from src.bot_logging import *
from src.timetable import *
from datetime import *


def with_zoom(message):
    if message is not None:
        words_in_message = message.split()
        for word in words_in_message:
            if word in zm.rooms:
                return message + " " + zm.channels[int(word)]
    return message


def text_message_for(num_of_group, time_of_start, message_):
    message_ = with_zoom(message_)
    bot.send_message(my_id, num_of_group + " " + time_of_start + " " + message_)


class CheckingTimetable(Table):
    def check_schedule(self):
        del_keys = []
        for key in self.time_of_class:
            cur_time = timedelta(hours=13, minutes=50, seconds=00)
            '''
            ct = datetime.now().time()
            cur_time = timedelta(hours=ct.hour, minutes=ct.minute, seconds=ct.second)
            '''
            start_time = datetime.strptime(key, '%H:%M')
            class_time = timedelta(hours=start_time.hour, minutes=start_time.minute, seconds=0)
            if 0 < (class_time - cur_time).total_seconds() < 900:  # засунуть в функцию
                for group, start in self.time_of_class[key]:
                    text_message_for(group, start,  self.day[group][start])
                del_keys.append(key)

        for del_key in del_keys:
            del self.time_of_class[del_key]  # pop есть

        '''
        text_message_for("6", '15:30', "говна поешь")
        '''


telegram_token = token

bot = telebot.TeleBot(telegram_token)
logging.basicConfig(level=logging.INFO)


@bot.message_handler(commands=['help', 'start'])
def help_message(message):
    save_message(message)
    bot.send_message(message.chat.id, '''
/help - все команды
''')


@bot.message_handler(content_types=['text'])
def send_text(message):
    if message.text == 'Привет':
        bot.send_message(message.chat.id, 'Привет, мой создатель')
    elif message.text == 'Пока':
        bot.send_message(message.chat.id, 'Прощай, создатель')
        print(message.chat.id)
    else:
        save_message(message)
        text_reversed = message.text[::-1]
        bot.send_message(message.chat.id, text_reversed)


@bot.message_handler(lambda message: True)
def another_message(message):
    help_message(message)


def schedule_loop(bot_):
    while 1:
        try:
            bot_.polling(none_stop=True)
        except Exception as exception:
            print(exception)


if __name__ == '__main__':
    # TODO: логгирование
    print('Start!\n')
    my_id = 794566071
    Thread(target=schedule_loop, args=(bot,)).start()
    while True:
        today = datetime.now()
        # TODO: пояснить ID = 794566071
        bot.send_message(my_id, today)
        # open timetable (Расписание осень 2020_2021.xlsx)
        wb = op.load_workbook("Расписание осень 2020_2021.xlsx")
        sheet_main = wb['Математика + МААД']
        cur_week_day = today.weekday()
        timetable = CheckingTimetable(cur_week_day, sheet_main)
        # make a dict of ZOOM id
        sheet_ZOOM = wb['ID zoom каналов']
        zm = Zoom(sheet_ZOOM)
        while today.day == datetime.now().day:
            timetable.check_schedule()

