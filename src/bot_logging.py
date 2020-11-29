from bot_system import *

PRINT = 1


def save_message(message):
    if PRINT:
        print(message)
    with open('../data/saved.txt', 'a') as f:
        f.write(f'{message.chat.id}: {message.text}\n')