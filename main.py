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
    if not (message.text is None):
        from_service = message.text.split(" ")
        if len(from_service) > 1 and from_service[0] == "/start" and from_service[1] in config.AVAILABLE_PLACES:
            from_service = from_service[1]
        else:
            from_service = "tg"

    if not users_db.isExist(User(message.from_user.id)):
        users_db.addUser(User(message.from_user.id, service=from_service))
    markup = types.InlineKeyboardMarkup(row_width=1)
    add_book = types.InlineKeyboardButton("Добавить книгу в расписание", callback_data="add_book")
    markup.add(add_book)
    bot.set_state(user_id=message.from_user.id, state=all_states.BotStates.start, chat_id=message.chat.id)
    bot.send_message(message.from_user.id, f'Привет, {message.from_user.first_name}', reply_markup=markup)


@bot.callback_query_handler(
    func=lambda call: bot.get_state(call.message.chat.id, call.from_user.id) == all_states.BotStates.start.name)
def call_back_handler(call: telebot.types.CallbackQuery):
    if call.data == "add_book":
        bot.set_state(call.message.chat.id, all_states.BotStates.add_book_name, call.message.chat.id)
        bot.send_message(chat_id=call.message.chat.id, text="Напишите название книги")
        users_db.activeUsers[call.message.chat.id].add_in_schedule(Schedule("", "", "", False))
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)


@bot.message_handler(
    func=lambda message: bot.get_state(message.chat.id, message.from_user.id) == all_states.BotStates.add_book_name.name)
def addBookName(message: telebot.types.Message):
    users_db.activeUsers[message.chat.id].schedule[len(users_db.activeUsers[message.chat.id].schedule)-1].book_name = message.text
    bot.set_state(message.from_user.id, all_states.BotStates.add_author, message.chat.id)
    bot.send_message(chat_id=message.chat.id, text="Напишите автора(ов) книги")


@bot.message_handler(
    func=lambda message: bot.get_state(message.chat.id, message.from_user.id) == all_states.BotStates.add_author.name)
def addAuthors(message: telebot.types.Message):
    users_db.activeUsers[message.chat.id].schedule[len(users_db.activeUsers[message.chat.id].schedule)-1].authors = message.text
    markup = types.InlineKeyboardMarkup(row_width=2)
    yes = types.InlineKeyboardButton("Да", callback_data="yes_read")
    no = types.InlineKeyboardButton("Нет", callback_data="no_read")
    markup.add(yes, no)
    bot.set_state(message.from_user.id, all_states.BotStates.add_read, message.chat.id)
    bot.send_message(chat_id=message.chat.id, text="Вы уже прочитали эту книгу", reply_markup=markup)


@bot.callback_query_handler(
    func=lambda call: bot.get_state(call.message.chat.id, call.from_user.id) == all_states.BotStates.add_read.name)
def isRead(call: telebot.types.CallbackQuery):
    if call.data == "yes_read":
        users_db.activeUsers[call.message.chat.id].schedule[len(users_db.activeUsers[call.message.chat.id].schedule)-1].is_read = True

        bot.set_state(call.message.chat.id, all_states.BotStates.add_esse, call.message.chat.id)
        bot.send_message(chat_id=call.message.chat.id, text="Напишите эссе")
    else:
        print("no")
        users_db.activeUsers[call.message.chat.id].schedule[len(users_db.activeUsers[call.message.chat.id].schedule)-1].is_read = False

        bot.set_state(call.message.chat.id, all_states.BotStates.start, call.message.chat.id)
        users_db.addShed(users_db.activeUsers[call.message.chat.id])
        for i in users_db.activeUsers[call.message.chat.id].schedule:
            print(i)
        # Добавить в расписание

@bot.message_handler(func=lambda message: bot.get_state(message.chat.id, message.from_user.id) == all_states.BotStates.add_esse.name)
def addEsse(message: telebot.types.Message):
    bot.set_state(message.from_user.id, all_states.BotStates.start, message.chat.id)
    users_db.activeUsers[message.chat.id].schedule[len(users_db.activeUsers[message.chat.id].schedule)-1].esse = message.text

    # Добавить в расписание с эссе
    for i in users_db.activeUsers[message.chat.id].schedule:
        print(i)
    users_db.addShed(users_db.activeUsers[message.chat.id])
    start(message)



bot.infinity_polling(skip_pending=True)
