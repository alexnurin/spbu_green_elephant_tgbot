#1)добавляем имя преподавателя в базу
'''
def add_telega_in_data_t(prepod, his_id):
    with sq.connect("teachers.db") as con:
        cur = con.cursor()
        cur.execute(f"""UPDATE teachers_mkn_1 SET teachers_authentication = '{his_id}' WHERE name= '{prepod}' """)'''