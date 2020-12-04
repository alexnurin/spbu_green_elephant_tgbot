import telebot
from src.bot_logging import *
from data.secret import token
import openpyxl as op
import pandas as pd
import pymorphy2
from datetime import *


# infinitive form for keywords
def infinitive_form(form):
    morph = pymorphy2.MorphAnalyzer()
    spec_chars = [",", "."]
    form = ''.join([ch for ch in form if ch not in spec_chars])
    form = form.lower()
    infinitive = morph.parse(form)[0].normal_form
    return infinitive


# correct line
def fix_line(line):
    n = len(line)
    key_words = ["лекция"]
    ignore_words = ["перерыв", "английский", "физический", "консультация"]
    for i in range(n):
        cell = line[i]
        if cell is not None:
            words_in_cell = cell.split()
            for word in words_in_cell:
                word = infinitive_form(word)
                if word in ignore_words:
                    for ind_cell in range(0, n):
                        line[ind_cell] = None
                    break
                # это много циклов - надо пофиксить (наверное)
                if word in key_words:
                    for ind_cell in range(i + 1, n):
                        line[ind_cell] = cell
                    break
    return line


# correct data
def fix_data(raw_data):
    for j in range(len(raw_data)):
        raw_data[j] = fix_line(raw_data[j])
    return raw_data


# check time format
def in_time_format(string):
    indices = [0, 1, 3, 4]
    if len(string) == 5:
        flag = True
        for i in indices:
            if not string[i].isdigit:
                flag = False
        if flag and (string[2] == "-" or string[2] == ":"):
            return True
    return False


# find time in description of class
def find_time_format(cell):
    pred_word = "$"
    key_alpha = ["с", "в", "-с"]
    if cell is not None:
        spec_chars = [",", ".", ")", "("]
        cell = ''.join([ch for ch in cell if ch not in spec_chars])
        words_in_cell = cell.split()
        for word in words_in_cell:
            if in_time_format(word) and pred_word in key_alpha:
                word = word[0:2] + ":" + word[3::]
                return word
            pred_word = word
        return None


class Table:
    def __init__(self, week_day, sheet):
        # TODO:relevant ID_numbers
        self.ID_numbers = [my_id]
        # set a week mods
        week = {0: (0, 1, 6),
                1: (0, 6, 11),
                2: (0, 11, 16),
                3: (1, 16, 21),
                4: (1, 21, 26),
                5: (0, 26, 31),
                6: (-1, -1, -1)}
        # read groups
        self.groups = [sheet.cell(row=1, column=i).value for i in range(3, 9)]
        # take into account the day of the week
        parity, low_line, high_line = week[week_day]
        # make short DataFrame for day from xlsx
        self.data = [[sheet.cell(row=2 * j + parity, column=i).value for i in range(3, 9)] for j in
                     range(low_line, high_line)]
        self.data = fix_data(self.data)
        self.time = [sheet.cell(row=2 * j + parity, column=2).value for j in range(low_line, high_line)]
        # make timetable for day
        self.day = pd.DataFrame(self.data, index=self.time, columns=self.groups)
        self.day.index.name = 'Время'
        self.day.columns.name = "Группы"
        # dict time
        self.time_of_class = {}
        # TODO:распарсить begin
        for group in self.groups:
            for start in self.time:
                info = self.day[group][start]
                if info is None:
                    continue
                begin = find_time_format(info)
                if begin is None:
                    begin = start[:5]
                if begin not in self.time_of_class:
                    self.time_of_class[begin] = [[group, start]]
                else:
                    self.time_of_class[begin].append([group, start])

    def make_a_newsletter(self, num_of_group, message_):
        for id_ in self.ID_numbers:
            bot.send_message(id_, num_of_group + " " + message_)

    def check_schedule(self):
        del_keys = []
        for key in self.time_of_class:
            # ct = datetime.now().time()
            # cur_time = timedelta(hours=ct.hour, minutes=ct.minute, seconds=ct.second)
            cur_time = timedelta(hours=13, minutes=50, seconds=00)
            start_time = datetime.strptime(key, '%H:%M')
            class_time = timedelta(hours=start_time.hour, minutes=start_time.minute, seconds=0)
            if 0 < (class_time - cur_time).total_seconds() < 900:  # засунуть в функцию
                for group, start in self.time_of_class[key]:
                    self.make_a_newsletter(group, with_zoom(self.day[group][start]))
                del_keys.append(key)

        for del_key in del_keys:
            del self.time_of_class[del_key]  # pop есть


'''||||||||||||||||||||||||| ZOOM |||||||||||||||||||||||||'''


def with_zoom(message):
    if message is not None:
        words_in_message = message.split()
        for word in words_in_message:
            if word in zm.rooms:
                return message + " " + zm.channels[int(word)]
    return message


class Zoom:
    def __init__(self, sheet):
        self.channels = {}
        self.rooms = []
        for j in range(2, 12 + 1):
            room = sheet.cell(row=j, column=1).value
            self.rooms.append(str(int(room)))
            id_ = sheet.cell(row=j, column=2).value
            self.channels[room] = id_


'''||||||||||||||||||||||||| BOT |||||||||||||||||||||||||'''

telegram_token = token

bot = telebot.TeleBot(telegram_token)


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


if __name__ == '__main__':
    # TODO: логгирование
    print('Start!\n')
    my_id = 794566071
    while True:
        # update info of the day
        today = datetime.now()
        # TODO: пояснить ID = 794566071
        bot.send_message(my_id, today)
        # open timetable (Расписание осень 2020_2021.xlsx)
        wb = op.load_workbook("Расписание осень 2020_2021.xlsx")
        sheet_main = wb['Математика + МААД']
        # input current day of week
        cur_week_day = today.weekday()
        # timetable = TimeTable(cur_week_day, sheet_main)
        timetable = Table(cur_week_day, sheet_main)
        # make a dict of ZOOM id
        sheet_ZOOM = wb['ID zoom каналов']
        zm = Zoom(sheet_ZOOM)
        # print(datetime.now().day)
        while today.day == datetime.now().day:
            timetable.check_schedule()
            # bot.send_message(my_id, "Пытаемся что-то отправить")
