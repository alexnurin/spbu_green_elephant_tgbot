from threading import Thread
import telebot
import openpyxl as op
from data.secret import token
from src.bot_logging import *
from src.timetable import *
from datetime import *
import sqlite3 as sq


'''
file_name = "students_spbu_real.db"


def get_telega_from_data(group):
    all_id_from_group = []
    for elem in group:
        with sq.connect(file_name) as con:
            cur = con.cursor()
            cur.execute(f"""SELECT telega_id FROM students_mkn WHERE student_group='{elem}' """)
            results = cur.fetchall()
            print(results)
            for i in range(len(results)):
                if results[i] != (0,):
                    all_id_from_group.append(results[i][0])
    return all_id_from_group


def add_telega_in_data(students_name, his_id):
    with sq.connect(file_name) as con:
        cur = con.cursor()
        cur.execute(f"""UPDATE students_mkn SET telega_id = '{his_id}' WHERE name= '{students_name}' """)
'''


def text_message_for(num_of_group, time_of_start, message_):
    message_ = with_zoom(message_)
    bot.send_message(developer_id, num_of_group + " " + time_of_start + " " + message_)


def with_zoom(message):
    if message is not None:
        words_in_message = message.split()
        for word in words_in_message:
            if word in zm.rooms:
                return message + " " + zm.channels[int(word)]
    return message


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
                    text_message_for(group, start, self.day[group][start])
                del_keys.append(key)

        for del_key in del_keys:
            del self.time_of_class[del_key]  # pop есть


telegram_token = token

bot = telebot.TeleBot(telegram_token)


@bot.message_handler(commands=['help'])
def help_message(message):
    save_message(message)
    bot.send_message(message.chat.id, '''
/help
/announce
/authorize
- все команды
''')


@bot.message_handler(commands=['authorize'])
def start_authorize(message):
    keyboard2 = telebot.types.ReplyKeyboardMarkup()
    keyboard2.row("Да", "Нет")
    sent = bot.send_message(message.chat.id, 'Вы хотите получать уведомления от бота?', reply_markup=keyboard2)
    bot.register_next_step_handler(sent, add_2_user_list)


def add_2_user_list(message):
    if message.text == "Да":
        bot.send_message(message.chat.id, "Пока нельзя!")
        print(message.chat.id)
    else:
        bot.send_message(message.chat.id, ":(")


@bot.message_handler(commands=['announce'])
def start_message(message):
    keyboard1 = telebot.types.ReplyKeyboardMarkup()
    keyboard1.row('20.Б01-мкн', '20.Б02-мкн', '20.Б03-мкн')
    keyboard1.row('20.Б04-мкн', '20.Б05-мкн', '20.Б06-мкн')
    keyboard1.row('все')
    if message.chat.id in masters_id:
        sent = bot.send_message(message.chat.id, 'Здравствуйте, если вы хотите сделать объявление, то '
                                                 'выберите, пожалуйста, группу', reply_markup=keyboard1)
        bot.register_next_step_handler(sent, send_text)
    else:
        bot.send_message(message.chat.id, 'У вас недостаточно прав, чтобы делать объявление :(')


def send_text(message):
    selected_group = []
    key_ans = ['20.Б01-мкн', '20.Б02-мкн', '20.Б03-мкн', '20.Б04-мкн', '20.Б05-мкн', '20.Б06-мкн', 'все']
    if message.text not in key_ans:
        bot.send_message(message.chat.id, 'вам нужно выбрать номер группы')
    elif message.text == 'все':
        selected_group = ['20.Б01-мкн', '20.Б02-мкн', '20.Б03-мкн', '20.Б04-мкн', '20.Б05-мкн', '20.Б06-мкн']
    else:
        selected_group = [message.text]
    sent = bot.send_message(message.chat.id, 'Напишите сообщения для групп')
    bot.register_next_step_handler(sent, selected_group, get_information)


def get_information(message, selected_group):
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
    masters_id = [794566071]
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

@bot.message_handler(lambda message: True)
def another_message(message):
    help_message(message)

"""
