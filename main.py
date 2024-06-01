import telebot

from telebot import types
from telebot.storage import StateMemoryStorage
from telebot import custom_filters


import config
import all_states
import users_db

from users_db import User
from users_db import Schedule

states = StateMemoryStorage()

bot = telebot.TeleBot(config.TOKEN, state_storage=states)

keyboard = telebot.types.ReplyKeyboardMarkup()
keyboard.row('/start')

if __name__ == '__main__':
    # Ignore previous(before start) messages from users
    bot.skip_pending = True

@bot.message_handler(commands=['start'])
def start(message: telebot.types.Message):
    from_service = []
    if not(message.text is None):
        from_service = message.text.split(" ")
        if len(from_service) > 1 and from_service[0] == "/start":
            from_service = from_service[1]
        else:
            from_service = "tg"

    bot.send_message(message.from_user.id, f'Привет, {message.from_user.first_name}')
    bot.set_state(user_id=message.from_user.id, state=all_states.BotStates.start, chat_id=message.chat.id)
    if not users_db.isExist(User(message.from_user.id)):
        users_db.addUser(User(message.from_user.id, service=from_service))


bot.infinity_polling(skip_pending=True)
