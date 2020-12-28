from threading import Thread
import telebot
import openpyxl as op
from datetime import *
from data.secret import token
from src.timetable import *
from src.Func_data_s import *
from src.bot_logging import *


def send_notifications(group, time_class, message):
    """
    The function sends notifications to registered students of the given group.
    :param str group: number of group in format - '20.Б0*-мкн'
    :param str time_class: time of class in format - '**:**'
    :param str message: message for sending
    """
    num_of_group = [int(group[5])]
    students_id_list = get_students_id_list(num_of_group)
    # process message
    message = make_message_with_zoom_id(message)
    for chat_id in students_id_list:
        try:
            bot.send_message(chat_id, '\n'.join([group, "Начало: " + time_class, message]))
            f_message_logger.debug(" ".join(['Сообщение с расписанием отправлено студенту c id',
                                            str(chat_id), 'из группы', group]))
        except Exception as exception:
            f_message_logger.critical('Сообщение о расписанием не было отправлено из-за ошибки ')
            f_message_logger.critical(exception)


def make_message_with_zoom_id(message: str) -> str:
    spec_chars = ["-"]
    if message is not None:
        words_in_message = message.split()
        for word in words_in_message:
            if word in zm.rooms:
                zoom_link = "https://zoom.us/j/" + "".join([ch for ch in zm.channels[word] if ch not in spec_chars])
                f_message_logger.info('Занятие: ' + message + " будет в zoom конференции.")
                return '\n'.join([message, "Идентификатор конференции: " + zm.channels[word], "Ссылка: " + zoom_link])
    f_message_logger.info('Занятие: ' + message + " будет НЕ в zoom конференции.")
    return message


# class for checking "Расписание осень 2020_2021.xlsx" and sending notifications
class CheckingTimetable(TimeTable):
    # check different with time of class and current time and send notifications to students
    def check_key(self, cur_key, diff, threshold):
        if 0 < diff < threshold:
            for group, start in self.time_of_class[cur_key]:
                send_notifications(group, cur_key, self.day[group][start])
            self.del_keys.append(cur_key)

    # delete sent notifications from dictionary with time of class
    def clear_from_sent(self, sent_notifications):
        for key in sent_notifications:
            self.time_of_class.pop(key)

    # compare current time with time in time_of_class
    def check_schedule(self):
        self.del_keys = []
        for key in self.time_of_class:
            ct = datetime.now().time()
            cur_time = timedelta(hours=ct.hour, minutes=ct.minute, seconds=ct.second)
            start_time = datetime.strptime(key, '%H:%M')
            class_time = timedelta(hours=start_time.hour, minutes=start_time.minute, seconds=0)
            self.check_key(key, (class_time - cur_time).total_seconds(), 900)
        self.clear_from_sent(self.del_keys)


telegram_token = token
bot = telebot.TeleBot(telegram_token)


# Handle '/start'
@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, '''Доброе время суток! 
Это бот для студентов 1-ого курса Математики и МААД.
Чтобы уведеть список команд,
нажмите
/help
''')


# Handle '/help'
@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, '''
- все команды
/announce - Сделать объявление студентам.
/authorize - Авторизоваться.
(зарегистрированный студент получает уведомления
о паре в своём расписании
за 15 минут до её непосредственного начала;
зарегистрированный преподаватель получает 
возможность делать объявления для зарегистрированных
студентов)
/get_links - получить полезные ссылки
''')


@bot.message_handler(commands=['authorize'])
def start_authorize(message):
    keyboard = telebot.types.ReplyKeyboardMarkup()
    keyboard.row("Я студент", "Я преподаватель", "Я/Мы МКН")
    sent = bot.send_message(message.chat.id, 'Ваш статус?', reply_markup=keyboard)
    bot.register_next_step_handler(sent, check_status)


def check_status(message):
    if message.text == "Я студент":
        keyboard = telebot.types.ReplyKeyboardMarkup()
        keyboard.row("Да",
                     "Хочу перестать",
                     "Я в этой жизни уже ничего не хочу...")
        sent = bot.send_message(message.chat.id, 'Хотите получать уведомления?', reply_markup=keyboard)
        bot.register_next_step_handler(sent, help_student)
    elif message.text == "Я преподаватель":
        sent = bot.send_message(message.chat.id, '''Введите ваш персональный пароль.
        (если ещё не получили: напишите @Anyfree8)''')
        bot.register_next_step_handler(sent, help_teacher)
    else:
        bot.send_message(message.chat.id, "Поздравляю!")


# interactive with students
def help_student(message):
    if message.text == "Да":
        if check_student_uniqueness(message.chat.id):
            sent = bot.send_message(message.chat.id, "Введите ваше настоящее ФИО\n"
                                                     "Например:\nЗубенко Михаил Петрович")
            bot.register_next_step_handler(sent, add_to_users)
        else:
            bot.send_message(message.chat.id, "Ваш id уже зарегистрирован!")
    elif message.text == "Хочу перестать":
        pop_from_users(message)
    else:
        bot.send_message(message.chat.id, ":(")


def add_to_users(message):
    name = message.text
    register_student(name, message.chat.id)
    bot.send_message(message.chat.id, "Готово!")


def pop_from_users(message):
    student_id = message.chat.id
    unregister_student(student_id)
    bot.send_message(message.chat.id, "Готово.")


# interactive with teachers
def help_teacher(message):
    done_add = register_teacher(message.chat.id, message.text)
    if done_add:
        bot.send_message(message.chat.id, "Готово!")
    else:
        bot.send_message(message.chat.id, "Простите, такой пароль отсутствует в базе!")


@bot.message_handler(commands=['announce'])
def start_message(message):
    keyboard = telebot.types.ReplyKeyboardMarkup()
    keyboard.row('20.Б01-мкн', '20.Б02-мкн', '20.Б03-мкн')
    keyboard.row('20.Б04-мкн', '20.Б05-мкн', '20.Б06-мкн')
    keyboard.row('все')
    is_teacher, teacher_name = get_teacher_name(message.chat.id)
    if is_teacher or message.chat.id in masters_id:
        sent = bot.send_message(message.chat.id, 'Здравствуйте, если вы хотите сделать объявление, то '
                                                 'выберите, пожалуйста, группу', reply_markup=keyboard)
        bot.register_next_step_handler(sent, send_text, teacher_name)
    else:
        bot.send_message(message.chat.id, 'У вас недостаточно прав, чтобы делать объявление :(')


def send_text(message, advertiser_name):
    selected_groups = []
    key_ans = ['20.Б01-мкн', '20.Б02-мкн', '20.Б03-мкн', '20.Б04-мкн', '20.Б05-мкн', '20.Б06-мкн', 'все']
    if message.text not in key_ans:
        bot.send_message(message.chat.id, 'Вам нужно выбрать номер группы.')
    elif message.text == 'все':
        selected_groups = [1, 2, 3, 4, 5, 6]
    else:
        selected_groups = [int(message.text[5])]
    sent = bot.send_message(message.chat.id, 'Напишите сообщения для групп')
    bot.register_next_step_handler(sent, get_information, selected_groups, advertiser_name)


def get_information(message, selected_groups, advertiser_name):
    students_id_list = get_students_id_list(selected_groups)
    for chat_id in students_id_list:
        try:
            bot.send_message(int(chat_id), '\n'.join([advertiser_name, message.text]))
        except Exception as exception:
            f_message_logger.critical(exception)


@bot.message_handler(commands=['get_links'])
def send_links(message):
    f = open('mkn_links.txt', 'r', encoding='utf-8')
    links = f.read()
    bot.send_message(message.chat.id, links)


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def redirect_user(message):
    bot.send_message(message.chat.id, ''' Нажмите /help,
чтобы уведеть список команд.
''')


def _polling(bot_):
    while 1:
        try:
            bot_.polling(none_stop=True)
        except Exception as exception:
            print(exception)


if __name__ == '__main__':
    f_message_logger.info('Start!!!')
    developer_id = 794566071
    masters_id = [794566071, 636998614]
    # communication with the user
    Thread(target=_polling, args=(bot,)).start()
    while True:
        today = datetime.now()
        cur_week_day = today.weekday()
        f_message_logger.info(today)
        # open timetable (Расписание осень 2020_2021.xlsx)
        workbook = op.load_workbook("Расписание осень 2020_2021.xlsx")
        sheet_main = workbook['Математика + МААД']
        timetable = CheckingTimetable(cur_week_day, sheet_main)
        # make a dict of ZOOM identifiers
        sheet_ZOOM = workbook['ID zoom каналов']
        zm = Zoom(sheet_ZOOM)
        while today.day == datetime.now().day:
            timetable.check_schedule()
