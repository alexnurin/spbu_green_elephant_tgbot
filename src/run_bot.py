from threading import Thread
import telebot
import openpyxl as op
import logging
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
    bot.send_message(developer_id, num_of_group + " " + time_of_start + " " + message_)


class CheckingTimetable(Table):
    def check_schedule(self):
        del_keys = []
        for key in self.time_of_class:
            # cur_time = timedelta(hours=13, minutes=50, seconds=00)
            # '''
            ct = datetime.now().time()
            cur_time = timedelta(hours=ct.hour, minutes=ct.minute, seconds=ct.second)
            # '''
            start_time = datetime.strptime(key, '%H:%M')
            class_time = timedelta(hours=start_time.hour, minutes=start_time.minute, seconds=0)
            if 0 < (class_time - cur_time).total_seconds() < 900:  # засунуть в функцию
                for group, start in self.time_of_class[key]:
                    text_message_for(group, start,  self.day[group][start])
                del_keys.append(key)

        for del_key in del_keys:
            del self.time_of_class[del_key]  # pop есть


telegram_token = token

bot = telebot.TeleBot(telegram_token)
# TODO: разобраться с логгированием
# logging.basicConfig(level=logging.INFO)


keyboard1 = telebot.types.ReplyKeyboardMarkup()
keyboard1.row('1', '2', '3')
keyboard1.row('4', '5', '6')
keyboard1.row('все')
selected_group = 0


@bot.message_handler(commands=['help'])
def help_message(message):
    save_message(message)
    bot.send_message(message.chat.id, '''
/help
/announce
- все команды
''')


@bot.message_handler(commands=['announce'])
def start_message(message):
    bot.send_message(message.chat.id, 'Здравствуйте, если вы хотите сделать объявление, то '
                                      'выберите, пожалуйста, группу', reply_markup=keyboard1)


@bot.message_handler(content_types=['text'])
def send_text(message):
    global selected_group
    key_ans = ['1', '2', '3', '4', '5', '6', 'все']
    if selected_group == 0:
        if message.text not in key_ans:
            bot.send_message(message.chat.id, 'вам нужно выбрать номер группы')
        elif message.text == 'все':
            selected_group = [1, 2, 3, 4, 5, 6]
        else:
            selected_group = int(message.text)
    sent = bot.send_message(message.chat.id, 'Напишите сообщения для групп')
    bot.register_next_step_handler(sent, get_information)


@bot.message_handler(content_types=['text'])
def get_information(message):
    if selected_group != 0:
        # for chat_id in [794566071, 636998614]:
        for chat_id in [794566071]:
            bot.send_message(chat_id, message.text)


def _polling(bot_):
    while 1:
        try:
            bot_.polling(none_stop=True)
        except Exception as exception:
            print(exception)


if __name__ == '__main__':
    # TODO: логгирование
    print('Start!\n')
    developer_id = 794566071
    Thread(target=_polling, args=(bot,)).start()
    while True:
        today = datetime.now()
        bot.send_message(developer_id, today)
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


"""
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

"""