#1)добавляем имя преподавателя в базу
import sqlite3 as sq
password=input()
id =input()
def add_telega_in_data_t(password, his_id):
    with sq.connect("teachers.db") as con:
        cur = con.cursor()
        cur.execute(f"""UPDATE teachers_mkn_1 SET teachers_authentication = '{his_id}' WHERE password_t= '{password}' """)
add_telega_in_data_t(password,id)