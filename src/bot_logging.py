import logging

logging.basicConfig(level='INFO', filename='BotLogFile.txt')
f_data_logger = logging.getLogger('База данных')
f_message_logger = logging.getLogger('Отправка сообщений')
f_bot_work_logger = logging.getLogger('Работа бота')
f_bot_work_logger.setLevel('WARNING')
