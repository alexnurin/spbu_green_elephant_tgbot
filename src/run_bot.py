from threading import Thread
import telebot
import openpyxl as op
import systemd
from datetime import *
from data.secret import token
from src.bot_logging import *
from src.timetable import *
from src.Func_data_s import *
# TODO: requirements.txt

# TODO: ('Connection aborted.', ConnectionResetError(10054, 'Удаленный хост принудительно разорвал существующее подключение', None, 10054, None))


def text_message_for(num_of_group, time_class, message_):
    cur_group = [int(num_of_group[5])]
    IDs = get_telega_from_data(cur_group)
    message_ = with_zoom(message_)
    for _id in IDs:
        bot.send_message(_id, num_of_group + "\n" + time_class + "\n" + message_)


def with_zoom(message):
    if message is not None:
        words_in_message = message.split()
        for word in words_in_message:
            if word in zm.rooms:
                return message + " " + zm.channels[int(word)]
    return message

# TODO: dangerous changes


class CheckingTimetable(Table):
    def check_key(self, cur_key, diff, threshold):
        if 0 < diff < threshold:  # засунуть в функцию
            for group, start in self.time_of_class[cur_key]:
                text_message_for(group, cur_key, self.day[group][start])
            self.del_keys.append(cur_key)

    def clear_from_sent(self, sent_notifications):
        for key in sent_notifications:
            self.time_of_class.pop(key)

    def check_schedule(self):
        self.del_keys = []
        for key in self.time_of_class:
            # cur_time = timedelta(hours=11, minutes=00, seconds=10)
            # '''
            ct = datetime.now().time()
            cur_time = timedelta(hours=ct.hour, minutes=ct.minute, seconds=ct.second)
            # '''
            start_time = datetime.strptime(key, '%H:%M')
            class_time = timedelta(hours=start_time.hour, minutes=start_time.minute, seconds=0)
            self.check_key(key, (class_time - cur_time).total_seconds(), 900)

        self.clear_from_sent(self.del_keys)


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
        keyboard2.row("Да",
                      "Хочу перестать",
                      "Я в этой жизни уже ничего не хочу...")
        sent = bot.send_message(message.chat.id, 'Хотите получать уведомления?', reply_markup=keyboard2)
        bot.register_next_step_handler(sent, help_student)
    elif message.text == "Я преподаватель":
        sent = bot.send_message(message.chat.id, 'Введите ваш персональный пароль.' + '\n' +
                                                 '(если ещё не получили: напишите @Anyfree8)')
        bot.register_next_step_handler(sent, help_teacher)
    else:
        bot.send_message(message.chat.id, "Поздравляю!")


# for students
def help_student(message):
    if message.text == "Да":
        if check_uniqueness(message.chat.id):
            sent = bot.send_message(message.chat.id, "Введите ваше ФИО")
            bot.register_next_step_handler(sent, add_to_users)
        else:
            bot.send_message(message.chat.id, "Ваш id уже зарегистрирован!")
    elif message.text == "Хочу перестать":
        pop_from_users(message)
    else:
        bot.send_message(message.chat.id, ":(")


def add_to_users(message):
    name = message.text
    add_telega_in_data(name, message.chat.id)
    bot.send_message(message.chat.id, "Готово!")


def pop_from_users(message):
    st_id = message.chat.id
    delete_telega_in_data(st_id)
    bot.send_message(message.chat.id, "Готово.")


# for teachers
def help_teacher(message):
    add_telega_in_data_t(message.chat.id, message.text)
    bot.send_message(message.chat.id, "Готово?!")


@bot.message_handler(commands=['announce'])
def start_message(message):
    keyboard1 = telebot.types.ReplyKeyboardMarkup()
    keyboard1.row('20.Б01-мкн', '20.Б02-мкн', '20.Б03-мкн')
    keyboard1.row('20.Б04-мкн', '20.Б05-мкн', '20.Б06-мкн')
    keyboard1.row('все')
    # TODO:подключение преподавателей
    is_teacher, teacher_name = get_teacher_name(message.chat.id)
    if is_teacher or message.chat.id in masters_id:
        sent = bot.send_message(message.chat.id, 'Здравствуйте, если вы хотите сделать объявление, то '
                                                 'выберите, пожалуйста, группу', reply_markup=keyboard1)
        bot.register_next_step_handler(sent, send_text, teacher_name)
    else:
        bot.send_message(message.chat.id, 'У вас недостаточно прав, чтобы делать объявление :(')


def send_text(message, advertiser_name):
    selected_group = []
    key_ans = ['20.Б01-мкн', '20.Б02-мкн', '20.Б03-мкн', '20.Б04-мкн', '20.Б05-мкн', '20.Б06-мкн', 'все']
    if message.text not in key_ans:
        bot.send_message(message.chat.id, 'Вам нужно выбрать номер группы.')
    elif message.text == 'все':
        selected_group = [1, 2, 3, 4, 5, 6]
    else:
        selected_group = [int(message.text[5])]
    sent = bot.send_message(message.chat.id, 'Напишите сообщения для групп')
    bot.register_next_step_handler(sent, get_information, selected_group, advertiser_name)


def get_information(message, selected_group, advertiser_name):
    IDs = []
    # TODO: убрать объявление для девелопера
    if len(selected_group) == 6:
        bot.send_message(developer_id, advertiser_name + "\n" + message.text)
    else:
        IDs = get_telega_from_data(selected_group)
    #
    for chat_id in IDs:
        bot.send_message(int(chat_id), advertiser_name + "\n" + message.text)


def _polling(bot_):
    while 1:
        try:
            bot_.polling(none_stop=True)
        except Exception as exception:
            print(exception)


if __name__ == '__main__':
    # TODO: логгирование
    print('Start!\n')
    # TODO: нормальный beta_mode
    beta_mode = False
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

        # print(timetable.time_of_class)

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
