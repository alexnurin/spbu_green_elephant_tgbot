from threading import Thread
import telebot
import openpyxl as op
from data.secret import token
from src.bot_logging import *
from src.timetable import *
from datetime import *
from src.Func_data_s import *


def text_message_for(num_of_group, time_class, message_):
    cur_group = [int(num_of_group[5])]
    IDs = get_telega_from_data(cur_group)
    message_ = with_zoom(message_)
    for _id in IDs:
        bot.send_message(_id, num_of_group + " " + time_class + " " + message_)


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
            # cur_time = timedelta(hours=8, minutes=50, seconds=00)
            # '''
            ct = datetime.now().time()
            cur_time = timedelta(hours=ct.hour, minutes=ct.minute, seconds=ct.second)
            # '''
            start_time = datetime.strptime(key, '%H:%M')
            class_time = timedelta(hours=start_time.hour, minutes=start_time.minute, seconds=0)
            if 0 < (class_time - cur_time).total_seconds() < 900:  # засунуть в функцию
                for group, start in self.time_of_class[key]:
                    text_message_for(group, key, self.day[group][start])
                del_keys.append(key)

        for del_key in del_keys:
            self.time_of_class.pop(del_key)  # pop есть?


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
    keyboard3 = telebot.types.ReplyKeyboardMarkup()
    keyboard3.row("Я студент", "Я преподаватель", "Я/Мы МКН")
    sent = bot.send_message(message.chat.id, 'Ваш статус?', reply_markup=keyboard3)
    bot.register_next_step_handler(sent, check_status)


def check_status(message):
    if message.text == "Я студент":
        keyboard2 = telebot.types.ReplyKeyboardMarkup()
        keyboard2.row("Да", "Нет")
        sent = bot.send_message(message.chat.id, 'Вы хотите получать уведомления от бота?', reply_markup=keyboard2)
        bot.register_next_step_handler(sent, add_2_user_list)
    elif message.text == "Я преподаватель":
        # bot.register_next_step_handler(sent, identification)
        bot.send_message(message.chat.id, "Не верю!")
    else:
        bot.send_message(message.chat.id, "Поздравляю!")


# for students
def add_2_user_list(message):
    if message.text == "Да":
        sent = bot.send_message(message.chat.id, "Введите ваше ФИО")
        bot.register_next_step_handler(sent, find_student)
    else:
        bot.send_message(message.chat.id, ":(")

# def del_from_user_list(message):


def find_student(message):
    name = message.text
    add_telega_in_data(name, message.chat.id)
    bot.send_message(message.chat.id, "Готово")


# for teachers
def identification(message):
    return


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
    global selected_group
    selected_group = []
    key_ans = ['20.Б01-мкн', '20.Б02-мкн', '20.Б03-мкн', '20.Б04-мкн', '20.Б05-мкн', '20.Б06-мкн', 'все']
    if message.text not in key_ans:
        bot.send_message(message.chat.id, 'вам нужно выбрать номер группы')
    elif message.text == 'все':
        selected_group = [1, 2, 3, 4, 5, 6]
    else:
        selected_group = [int(message.text[5])]
    sent = bot.send_message(message.chat.id, 'Напишите сообщения для групп')
    bot.register_next_step_handler(sent, get_information)


def get_information(message):
    IDs = get_telega_from_data(selected_group)
    for chat_id in IDs:
        bot.send_message(int(chat_id), message.text)


def _polling(bot_):
    while 1:
        try:
            bot_.polling(none_stop=True)
        except Exception as exception:
            print(exception)


if __name__ == '__main__':
    selected_group = []
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
