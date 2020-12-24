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


# 5.1)
def add_telega_in_data_t(_id, password):
    with sq.connect("teachers (2).db") as con:
        cur = con.cursor()
        cur.execute(f"""SELECT name FROM teachers_mkn_1 WHERE password_t= '{password}' """)
        results = cur.fetchall()
        if results:
            cur.execute(
                f"""UPDATE teachers_mkn_1 SET teachers_authentication = '{_id}' WHERE password_t= '{password}' """)
            return True
        else:
            return False


# add_telega_in_data_t(91717534, "fghj6L-qaer5M-83dSzc")


# 5.1)
def delete_telega_in_data_t(teacher_id):
    with sq.connect("teachers (2).db") as con:
        cur = con.cursor()
        cur.execute(f"""UPDATE teachers_mkn_1 SET teachers_authentication = '{0}' 
                    WHERE teachers_authentication= '{teacher_id}' """)


# delete_telega_in_data_t(794566071)


# 6
def get_teacher_name(teacher_id):
    with sq.connect("teachers (2).db") as con:
        cur = con.cursor()
        cur.execute(f"""SELECT name FROM teachers_mkn_1 WHERE teachers_authentication='{teacher_id}' """)
        results = cur.fetchall()
        if results:
            return True, results[0][0]
        else:
            return False, "developer"

# add_telega_in_data("Копейкина Софья Евгеньевна", 669531883)


def new_password(name_, password):
    with sq.connect("teachers (2).db") as con:
        cur = con.cursor()
        cur.execute(f"""UPDATE teachers_mkn_1 SET password_t = '{password}' 
                           WHERE name = '{name_}' """)
#fghj6L-qaer5M-83dSzc

# new_password('Максимов', "fghj6L-qaer5M-83dSzc")