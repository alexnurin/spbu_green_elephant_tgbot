import openpyxl as op
import pandas as pd


# open timetable (Расписание осень 2020_2021.xlsx)
wb = op.load_workbook("monday.xlsx")


# make a dict of ZOOM id
sheet_ZOOM = wb['ID ZOOM каналов']
ZOOM_channels = {}
rooms = []
for j in range(2, 12 + 1):
    room = sheet_ZOOM.cell(row=j, column=1).value
    rooms.append(str(room))
    id_ = sheet_ZOOM.cell(row=j, column=2).value
    ZOOM_channels[room] = id_


# make short DataFrame for Monday from toy xlsx
sheet = wb['Математика + МААД']
data = [[sheet.cell(row=2*j, column=i).value for i in range(3, 9)] for j in range(1, 6)]
time = [sheet.cell(row=2*j, column=2).value for j in range(1, 6)]
groups = [sheet.cell(row=1, column=i).value for i in range(3, 9)]
df = pd.DataFrame(data, index=time, columns=groups)
df.index.name = 'Время'
df.columns.name = "Группы"
# info = df['20.Б06-мкн']['15:25 - 17:00']


# output number of group, ZOOM channel, ZOOM id, if it`s necessary for current time
def who_want_to_zoom(cur_time):
    for group in groups:
        cell = df[group][cur_time]
        if cell is not None:
            words_in_cell = cell.split()
            for word in words_in_cell:
                if word in rooms:
                    print(cur_time, group, word, ZOOM_channels[int(word)])
                    break

#  df.loc[11:15 - 12:50]
