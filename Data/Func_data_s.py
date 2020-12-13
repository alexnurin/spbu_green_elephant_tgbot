
#Functions for students
#1)
'''удаляет телеграмм из базы студентов(принимает имя студента,как в таблице)
def delete_telega_in_data(students_name):
    with sq.connect("students_spbu_real.db") as con:
        cur = con.cursor()
        cur.execute(f"""UPDATE students_mkn SET telega_id = '{0}' WHERE name= '{students_name}' """)
'''
#2)
#получает номер группы и возвращает массив с айдишниками телеграммов
'''def get_telega_from_data(group):
    all_id_from_group = []
    for elem in group:
        with sq.connect("students_spbu_real.db") as con:
            cur = con.cursor()
            cur.execute(f"""SELECT telega_id FROM students_mkn WHERE student_group='{elem}' """)
            results = cur.fetchall()
            for i in range(len(results)):
                if results[i] != ('0',):
                    all_id_from_group.append(results[i][0])
    return all_id_from_group
#3)
#Получает имя студента ,как в таблице , и его айдишник .Добавляет телеграмм студента в базу студнтов
import sqlite3 as sq
name =input()
id=input()

def add_telega_in_data(students_name, his_id):
    with sq.connect("students_spbu_real.db") as con:
        cur = con.cursor()
        cur.execute(f"""UPDATE students_mkn SET telega_id = '{his_id}' WHERE name= '{students_name}' """)
add_telega_in_data(name,id)
name =input()
id=input()
add_telega_in_data(name,id)
name =input()
id=input()
add_telega_in_data(name,id)
group=[1]
print(get_telega_from_data(group))'''
