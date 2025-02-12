import pandas as pd
import pymorphy2


# infinitive form for keywords
def make_infinitive_form(form: str) -> str:
    morph = pymorphy2.MorphAnalyzer()
    spec_chars = [",", "."]
    form = ''.join([ch for ch in form if ch not in spec_chars])
    form = form.lower()
    infinitive = morph.parse(form)[0].normal_form
    return infinitive


# correct line
def fix_line(line: list) -> list:
    """
    Function completes row to the end with current cell if a keyword is found.
    If ignore word is found it fulls all row with None.
    :param line: line from xlsx table
    :return line : fixed line
    """
    n = len(line)
    key_words = ["лекция", "дополнительный"]
    ignore_words = ["перерыв", "английский", "физический", "консультация"]
    for i in range(n):
        cell = line[i]
        if cell is not None:
            words_in_cell = cell.split()
            for word in words_in_cell:
                word = make_infinitive_form(word)
                if word in key_words:
                    # full line as cell
                    for ind_cell in range(i + 1, n):
                        line[ind_cell] = cell
                    return line
                if word in ignore_words:
                    # make line empty
                    for ind_cell in range(0, n):
                        line[ind_cell] = None
                    return line
    return line


# correct data with fix_line
def fix_data(raw_data: list) -> list:
    for j in range(len(raw_data)):
        raw_data[j] = fix_line(raw_data[j])
    return raw_data


# check for time format
def is_in_time_format(applicant: str) -> bool:
    spec_chars = [":", "-"]
    length = len(applicant)
    if length == 5 and applicant[2] in spec_chars:
        for i in range(length):
            if i != 2 and not applicant[i].isdigit:
                return False
        return True
    else:
        return False


# find time in description of class
def find_time_format(cell):
    pred_word = "$"
    key_alpha = ["с", "в", "-с", "С"]
    if cell is not None:
        spec_chars = [",", ".", ")", "("]
        cell = ''.join([ch for ch in cell if ch not in spec_chars])
        words_in_cell = cell.split()
        for word in words_in_cell:
            if is_in_time_format(word) and pred_word in key_alpha:
                word = word[0:2] + ":" + word[3::]
                return word
            pred_word = word
        return None


# make a timetable information
class TimeTable:
    def __init__(self, week_day, sheet):
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
        parity, low_line, high_line = week[week_day]
        # make short DataFrame for day from xlsx
        self.data = [[sheet.cell(row=2 * j + parity, column=i).value
                      for i in range(3, 9)]
                     for j in range(low_line, high_line)]
        self.data = fix_data(self.data)
        self.time = [sheet.cell(row=2 * j + parity, column=2).
                     value for j in range(low_line, high_line)]
        # make timetable for day
        self.day = pd.DataFrame(self.data,
                                index=self.time,
                                columns=self.groups)
        self.day.index.name = 'Время'
        self.day.columns.name = "Группы"
        # dict time
        self.time_of_class = {}
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
        # list keys in time of class to be deleted
        self.del_keys = []


# make a ZOOM id information
class Zoom:
    def __init__(self, sheet):
        self.channels = {}
        self.rooms = []
        for j in range(2, 12 + 1):
            room = str(int(sheet.cell(row=j, column=1).value))
            self.rooms.append(room)
            id_ = sheet.cell(row=j, column=2).value
            self.channels[room] = id_
