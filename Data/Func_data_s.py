import sqlite3 as sq

table_name = "students_spbu_real (5).db"

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
    with sq.connect(table_name) as con:
        cur = con.cursor()
        cur.execute(f"""UPDATE students_mkn SET telega_id = '{0}' WHERE telega_id= '{student_id}' """)


# 2)
# получает номер группы и возвращает массив с айдишниками телеграммов
def get_telega_from_data(groups):
    all_id_from_group = []
    for group in groups:
        with sq.connect(table_name) as con:
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
    with sq.connect(table_name) as con:
        cur = con.cursor()
        cur.execute(f"""UPDATE students_mkn SET telega_id = '{his_id}' WHERE name= '{students_name}' """)


# 4)
# Проверка уникальности id студента, который хочет зарегистрироваться
def check_uniqueness(student_id):
    with sq.connect(table_name) as con:
        cur = con.cursor()
        cur.execute(f"""SELECT telega_id FROM students_mkn WHERE telega_id='{str(student_id)}' """)
        results = cur.fetchall()
        if results:
            return False
        else:
            return True


# 5)
# Получает имя студента и выдает ближайшее имя в таблице соответствующее этому

'''








'''


def distance(wrong_name, name, len_wrong_name):
    len_name = len(name)
    name = '0' + name
    array_of_matches = []
    for i in range(len_name + 1):
        W = []
        for j in range(len_wrong_name + 1):
            W.append((max(len_name, len_wrong_name) + 1))
        array_of_matches.append(W)
    for i in range(len_wrong_name + 1):
        array_of_matches[0][i] = i
    for i in range(len_name + 1):
        array_of_matches[i][0] = i
    for i in range(1, len_name + 1):
        for j in range(1, len_wrong_name + 1):
            if wrong_name[j] == name[i]:
                array_of_matches[i][j] = array_of_matches[i - 1][j - 1]
            else:
                array_of_matches[i][j] = 1 + min(array_of_matches[i - 1][j], array_of_matches[i - 1][j - 1],
                                                 array_of_matches[i][j - 1])
    number_of_matches = array_of_matches[len_name][len_wrong_name]
    return number_of_matches


def chek_name(wrong_name):
    with sq.connect("students_spbu_real.db") as con:
        cur = con.cursor()
        cur.execute(f"""SELECT name FROM students_mkn  """)
        results = cur.fetchall()
        names = []
        for i in range(len(results)):
            names.append(results[i][0])
    len_wrong_name = len(wrong_name)
    wrong_name = '0' + wrong_name
    nearest_name = '0'
    max_difference = 10000000
    for k in range(len(names)):
        name_0 = names[k]
        number_of_matches = distance(wrong_name, name_0, len_wrong_name)
        if number_of_matches <= 11 and number_of_matches < max_difference:
            max_difference = number_of_matches
            nearest_name = names[k]
    if max_difference <= 11:
        return nearest_name
    else:
        return 0

'''def chek_name(wrong_name):
    with sq.connect("students_spbu_real.db") as con:
        cur = con.cursor()
        cur.execute(f"""SELECT name FROM students_mkn  """)
        results = cur.fetchall()
        names = []
        for i in range(len(results)):
            names.append(results[i][0])
    len_wrong_name = len(wrong_name)
    wrong_name = '0' + wrong_name
    nearest_name = '0'
    max_difference = 10000000
    for k in range(len(names)):
        name_0 = names[k]
        len_name = len(name_0)
        name_0 = '0' + name_0
        array_of_matches = []
        for i in range(len_name + 1):
            W = []
            for j in range(len_wrong_name + 1):
                W.append((max(len_name, len_wrong_name) + 1))
            array_of_matches.append(W)
        for i in range(len_wrong_name + 1):
            array_of_matches[0][i] = i
        for i in range(len_name + 1):
            array_of_matches[i][0] = i
        for i in range(1, len_name + 1):
            for j in range(1, len_wrong_name + 1):
                if wrong_name[j] == name_0[i]:
                    array_of_matches[i][j] = array_of_matches[i - 1][j - 1]
                else:
                    array_of_matches[i][j] = 1 + min(array_of_matches[i - 1][j], array_of_matches[i - 1][j - 1],
                                                     array_of_matches[i][j - 1])
        number_of_matches = array_of_matches[len_name][len_wrong_name]
        if number_of_matches <= 5 and number_of_matches < max_difference:
            max_difference = number_of_matches
            nearest_name = names[k]
    if max_difference <= 5:
        return nearest_name
    else:
        return 0'''
