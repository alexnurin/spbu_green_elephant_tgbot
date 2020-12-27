from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from src.bot_logging import *

engine_students = create_engine('sqlite:///students_spbu_real (5).db', echo=True)
engine_teachers = create_engine('sqlite:///teachers (2).db', echo=True)
meta_students = MetaData(engine_students)
meta_teachers = MetaData(engine_teachers)
students = Table(
    'students_mkn', meta_students,
    Column('students_id', Integer, primary_key=True),
    Column('name', String),
    Column('student_group', Integer),
    Column('english_group', Integer),
    Column('telega_id', String, default=0)
)

teachers = Table(
    'teachers_mkn_1', meta_teachers,
    Column('teachers_authentication', Integer, default=0),
    Column('name', String),
    Column('teaching_group', Integer, default=1),
    Column('subject', String),
    Column('password_t', Integer, default=0)
)


# add student to "students_spbu_real (5).db"
def register_student(students_name: str, student_id: int):
    conn = engine_students.connect()
    stmt = students.update().where(students.c.name == students_name).values(telega_id=str(student_id))
    conn.execute(stmt)
    f_data_logger.info('Зарегистрировался студент: ' + students_name + '. id: ' + str(student_id))


# delete student from "students_spbu_real (5).db"
def unregister_student(student_id: int):
    conn = engine_students.connect()
    stmt = students.update().where(students.c.telega_id == str(student_id)).values(telega_id='0')
    conn.execute(stmt)
    f_data_logger.info('Отписался студент с id: ' + str(student_id))


# Checking the uniqueness of the id of the student who wants to register
def check_student_uniqueness(student_id: int) -> bool:
    results_empty = True
    conn = engine_students.connect()
    s = students.select().where(students.c.telega_id == str(student_id))
    results = conn.execute(s)
    # check for emptiness
    for value in results:
        results_empty = False
        break
    if results_empty:
        f_data_logger.info('Студент c id: ' + str(student_id) + ' прошел проверку на уникальность')
        return True
    else:
        f_data_logger.info('Попытка повторной регистрации c id: ' + str(student_id))
        return False


# gets a list of student ids from given groups
def get_students_id_list(groups: list) -> list:
    """
    :param groups: list with numbers of groups
    :return all_id_from_groups:  list with id for each student from input groups
    """
    all_id_from_groups = []
    conn = engine_students.connect()
    for group in groups:
        s = students.select().where(students.c.student_group == group)
        results = conn.execute(s)
        for value in results:
            if value[4] != '0':
                all_id_from_groups.append(value[4])
    f_data_logger.info(f'id студентов из групп/группы {groups} были выбраны из базы данных')
    return all_id_from_groups


# register teacher by password (that is add teacher id to "teachers (2).db")
def register_teacher(user_id: int, password: str):
    """
    :return bool: True if user is teacher and False otherwise
    """
    results_empty = True
    conn = engine_teachers.connect()
    s = teachers.select().where(teachers.c.password_t == password)
    results = conn.execute(s)
    for value in results:
        results_empty = False
    if not results_empty:
        stmt = teachers.update().where(teachers.c.password_t == password).values(teachers_authentication=user_id)
        conn.execute(stmt)
        f_data_logger.info('Преподаватель  с id: ' + str(user_id) + ' зарегистрирован')
        return True
    else:
        f_data_logger.info('Пароль ' + password + ' не найден')
        return False


# recognize teacher by id
def get_teacher_name(teacher_id: int):
    """
    :return: True and str name of teacher if teacher was register
    """
    teacher_name = "None"
    conn = engine_teachers.connect()
    s = teachers.select().where(teachers.c.teachers_authentication == teacher_id)
    results = conn.execute(s)
    for value in results:
        teacher_name = value[1]
    if teacher_name != "None":
        f_data_logger.info('Найдено имя преподавателя: ' + teacher_name)
        return True, teacher_name
    else:
        f_data_logger.info('Имя не найдено, id: ' + str(teacher_id))
        return False, "developer"

