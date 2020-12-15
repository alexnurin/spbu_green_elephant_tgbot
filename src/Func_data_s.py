import sqlite3 as sq

# Functions for students


# 1)
# удаляет телеграмм из базы студентов(принимает имя студента,как в таблице)
'''
def delete_telega_in_data(students_name):
    with sq.connect(table_name) as con:
        cur = con.cursor()
        cur.execute(f"""UPDATE students_mkn SET telega_id = '{0}' WHERE name= '{students_name}' """)
'''


# 1.1)
def delete_telega_in_data(student_id):
    with sq.connect("students_spbu_real (5).db") as con:
        cur = con.cursor()
        cur.execute(f"""UPDATE students_mkn SET telega_id = '{0}' WHERE telega_id= '{student_id}' """)


# 2)
# получает номер группы и возвращает массив с айдишниками телеграммов
def get_telega_from_data(groups):
    all_id_from_group = []
    for group in groups:
        with sq.connect("students_spbu_real (5).db") as con:
            cur = con.cursor()
            cur.execute(f"""SELECT telega_id FROM students_mkn WHERE student_group='{group}' """)
            results = cur.fetchall()
            for i in range(len(results)):
                if results[i] != ('0',):
                    all_id_from_group.append(results[i][0])
    return all_id_from_group


# 3)
# Получает имя студента ,как в таблице , и его айдишник .Добавляет телеграмм студента в базу студнтов
def add_telega_in_data(students_name, his_id):
    with sq.connect("students_spbu_real (5).db") as con:
        cur = con.cursor()
        cur.execute(f"""UPDATE students_mkn SET telega_id = '{his_id}' WHERE name= '{students_name}' """)


# 4)
# Проверка уникальности id студента, который хочет зарегистрироваться
def check_uniqueness(student_id):
    with sq.connect("students_spbu_real (5).db") as con:
        cur = con.cursor()
        cur.execute(f"""SELECT telega_id FROM students_mkn WHERE telega_id='{str(student_id)}' """)
        results = cur.fetchall()
        if results:
            return False
        else:
            return True


# 5)

# add_telega_in_data("Копейкина Софья Евгеньевна", 669531883)
