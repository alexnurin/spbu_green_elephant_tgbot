import sqlite3 as sq


# add student to "students_spbu_real (5).db"
def register_student(students_name: str, student_id: int):
    with sq.connect("students_spbu_real (5).db") as con:
        cur = con.cursor()
        cur.execute(f"""UPDATE students_mkn SET telega_id = '{student_id}' WHERE name= '{students_name}' """)


# delete student from "students_spbu_real (5).db"
def unregister_student(student_id: int):
    with sq.connect("students_spbu_real (5).db") as con:
        cur = con.cursor()
        cur.execute(f"""UPDATE students_mkn SET telega_id = '{0}' WHERE telega_id= '{student_id}' """)


# Checking the uniqueness of the id of the student who wants to register
def check_student_uniqueness(student_id: int) -> bool:
    with sq.connect("students_spbu_real (5).db") as con:
        cur = con.cursor()
        cur.execute(f"""SELECT telega_id FROM students_mkn WHERE telega_id='{str(student_id)}' """)
        results = cur.fetchall()
        if results:
            return False
        else:
            return True


# gets a list of student ids from given groups
def get_students_id_list(groups: list) -> list:
    """
    :param groups: list with numbers of groups
    :return all_id_from_groups:  list with id for each student from input groups
    """
    all_id_from_groups = []
    for group in groups:
        with sq.connect("students_spbu_real (5).db") as con:
            cur = con.cursor()
            cur.execute(f"""SELECT telega_id FROM students_mkn WHERE student_group='{group}' """)
            results = cur.fetchall()
            for i in range(len(results)):
                if results[i] != ('0',):
                    all_id_from_groups.append(results[i][0])
    return all_id_from_groups


# register teacher by password (that is add teacher id to "teachers (2).db")
def register_teacher(user_id: int, password: str):
    """
    :return bool: True if user is teacher and False otherwise
    """
    with sq.connect("teachers (2).db") as con:
        cur = con.cursor()
        cur.execute(f"""SELECT name FROM teachers_mkn_1 WHERE password_t= '{password}' """)
        results = cur.fetchall()
        if results:
            cur.execute(
                f"""UPDATE teachers_mkn_1 SET teachers_authentication = '{user_id}' WHERE password_t= '{password}' """)
            return True
        else:
            return False


# recognize teacher by id
def get_teacher_name(teacher_id: int):
    """
    :return: True and str name of teacher if teacher was register
    """
    with sq.connect("teachers (2).db") as con:
        cur = con.cursor()
        cur.execute(f"""SELECT name FROM teachers_mkn_1 WHERE teachers_authentication='{teacher_id}' """)
        results = cur.fetchall()
        if results:
            return True, results[0][0]
        else:
            return False, "developer"


