import openpyxl as op
import pandas as pd
import pymorphy2


morph = pymorphy2.MorphAnalyzer()
# open timetable (Расписание осень 2020_2021.xlsx)
wb = op.load_workbook("Расписание осень 2020_2021.xlsx")


# infinitive form for keywords
def infinitive_form(form):
    """
    :param form: arbitrary form of word
    :return: infinitive
    """
    spec_chars = [","]
    form = ''.join([ch for ch in form if ch not in spec_chars])
    form = form.lower()
    p = morph.parse(form)[0].normal_form
    return p


# output number of group, ZOOM channel, ZOOM id, if it`s necessary for current time
def who_want_to_zoom(cur_time, day):
    for group in groups:
        cell = day[group][cur_time]
        if cell is not None:
            words_in_cell = cell.split()
            for word in words_in_cell:
                if word in rooms:
                    print(cur_time, group, word, ZOOM_channels[int(word)])
                    break


# correct data
def lecture_correct(data):
    first_cell = data[0]
    if first_cell is not None:
        words_in_cell = first_cell.split()
        for word in words_in_cell:
            if infinitive_form(word) == "лекция":
                for ind_cell in range(1, len(data)):
                    data[ind_cell] = first_cell
                break
    return data


# make a dict of ZOOM id
sheet_ZOOM = wb['ID zoom каналов']
ZOOM_channels = {}
rooms = []
for j in range(2, 12 + 1):
    room = sheet_ZOOM.cell(row=j, column=1).value
    rooms.append(str(int(room)))
    id_ = sheet_ZOOM.cell(row=j, column=2).value
    ZOOM_channels[room] = id_


# open timetable
sheet = wb['Математика + МААД']
groups = [sheet.cell(row=1, column=i).value for i in range(3, 9)]


# make short DataFrame for Monday from toy xlsx
data_md = [[sheet.cell(row=2*j, column=i).value for i in range(3, 9)] for j in range(1, 6)]
time_md = [sheet.cell(row=2*j, column=2).value for j in range(1, 6)]
md = pd.DataFrame(data_md, index=time_md, columns=groups)
md.index.name = 'Время'
md.columns.name = "Группы"
# info = df['20.Б06-мкн']['15:25 - 17:00']


# make short DataFrame for Tuesday from toy xlsx
data_td = [[sheet.cell(row=2*j, column=i).value for i in range(3, 9)] for j in range(6, 11)]
time_td = [sheet.cell(row=2*j, column=2).value for j in range(6, 11)]
td = pd.DataFrame(data_td, index=time_td, columns=groups)
td.index.name = 'Время'
td.columns.name = "Группы"


# make short DataFrame for Wednesday from toy xlsx
data_wd = [[sheet.cell(row=2*j, column=i).value for i in range(3, 9)] for j in range(11, 16)]

for j in range(len(data_wd)):
    data_wd[j] = lecture_correct(data_wd[j])

time_wd = [sheet.cell(row=2*j, column=2).value for j in range(11, 16)]
wd = pd.DataFrame(data_wd, index=time_wd, columns=groups)
wd.index.name = 'Время'
wd.columns.name = "Группы"
# who_want_to_zoom('13:40 - 15:15', wd)


# make short DataFrame for Thursday from toy xlsx
data_thd = [[sheet.cell(row=2*j + 1, column=i).value for i in range(3, 9)] for j in range(16, 21)]
time_thd = [sheet.cell(row=2*j + 1, column=2).value for j in range(16, 21)]
thd = pd.DataFrame(data_thd, index=time_thd, columns=groups)
thd.index.name = 'Время'
thd.columns.name = "Группы"


# make short DataFrame for Friday from toy xlsx
data_fd = [[sheet.cell(row=2*j + 1, column=i).value for i in range(3, 9)] for j in range(21, 26)]
time_fd = [sheet.cell(row=2*j + 1, column=2).value for j in range(21, 26)]
fd = pd.DataFrame(data_fd, index=time_fd, columns=groups)
fd.index.name = 'Время'
fd.columns.name = "Группы"


# make short DataFrame for Saturday from toy xlsx
data_sd = [[sheet.cell(row=2*j, column=i).value for i in range(3, 9)] for j in range(26, 31)]
time_sd = [sheet.cell(row=2*j, column=2).value for j in range(26, 31)]
sd = pd.DataFrame(data_sd, index=time_sd, columns=groups)
sd.index.name = 'Время'
sd.columns.name = "Группы"
