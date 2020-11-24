import telebot
import secret
from bot_logging import *
from bot_system import *
telegram_token = secret.token

bot = telebot.TeleBot(telegram_token)


@bot.message_handler(commands=['help', 'start'])
def help_message(message):
    save_message(message)
    bot.send_message(message.chat.id, '''
/help - все команды
''')


@bot.message_handler(content_types=['text'])
def text_message(message):
    save_message(message)
    text_reversed = message.text[::-1]
    bot.send_message(message.chat.id, text_reversed)


@bot.message_handler(lambda message: True)
def another_message(message):
    help_message(message)


if __name__ == '__main__':
    print('Start!\n')
    while 1:
        try:
            bot.polling(none_stop=True)
        except Exception as exception:
            print(exception)
