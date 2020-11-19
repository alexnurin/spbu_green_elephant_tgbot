import openpyxl as op
import pandas as pd
import itertools

# open timetable (Расписание осень 2020_2021.xlsx)
wb = op.load_workbook("time_table.xlsx")

# make a dict of ZOOM id
sheet_ZOOM = wb.get_sheet_by_name('ID ZOOM каналов')
ZOOM_channels = {}
for j in range(2, 12 + 1):
    room = sheet_ZOOM.cell(row=j, column=1).value
    id_ = sheet_ZOOM.cell(row=j, column=2).value
    ZOOM_channels[room] = id_


# make short DataFrame for Monday from toy xlsx
sheet = wb.get_sheet_by_name('Математика + МААД')
data = [[cell.value for cell in cellObj] for cellObj in sheet['C2':'D6']]
time = [sheet.cell(row=i, column=2).value for i in range(2, 7)]
groups = [sheet.cell(row=1, column=i).value for i in range(3, 5)]
df = pd.DataFrame(data, index=time, columns=groups)
df.index.name = 'Время'
df.columns.name = "Группы"
info = df['20.Б06-мкн']['15:25 - 17:00']


