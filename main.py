import math

import telebot

from telebot import types
from telebot.apihelper import ApiException
from telebot.storage import StateMemoryStorage

import config
import all_states
import user
import users_db
import ai_requests

from users_db import User
from users_db import Schedule

import texts

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
        users_db.addUser(User(message.from_user.id, service=from_service, language=message.from_user.language_code))
    markup = types.InlineKeyboardMarkup(row_width=2)
    add_book = types.InlineKeyboardButton(texts.add_book_to_schedule[users_db.activeUsers[message.chat.id].language], callback_data="add_book")
    check_ = types.InlineKeyboardButton(texts.my_schedule[users_db.activeUsers[message.chat.id].language], callback_data="check_books")
    get_help = types.InlineKeyboardButton(texts.book_advice[users_db.activeUsers[message.chat.id].language], callback_data="find_book")
    get_list_by_file = types.InlineKeyboardButton(texts.download_list[users_db.activeUsers[message.chat.id].language], callback_data="download")
    ru = types.InlineKeyboardButton("🇷🇺", callback_data="ru")
    en = types.InlineKeyboardButton("🇺🇸", callback_data="en")
    markup.add(add_book)
    markup.add(check_)
    markup.add(get_help)
    markup.add(get_list_by_file)
    markup.add(ru, en)
    bot.set_state(user_id=message.from_user.id, state=all_states.BotStates.start, chat_id=message.chat.id)
    bot.send_message(message.from_user.id, f'{texts.hello[users_db.activeUsers[message.chat.id].language]} {", " * int(message.from_user.first_name != "")}{message.from_user.first_name}', reply_markup=markup)

@bot.callback_query_handler(
    func=lambda call: bot.get_state(call.message.chat.id, call.from_user.id) == all_states.BotStates.start.name)
def call_back_handler(call: telebot.types.CallbackQuery):
    if call.data == "add_book":
        bot.set_state(call.message.chat.id, all_states.BotStates.add_book_name, call.message.chat.id)
        bot.send_message(chat_id=call.message.chat.id, text=texts.write_book_name[users_db.activeUsers[call.message.chat.id].language])
        users_db.activeUsers[call.message.chat.id].add_in_schedule(Schedule("", "", "", False))
        try:
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        except ApiException:
            print("Error")
    elif call.data == "find_book":
        bot.set_state(call.message.chat.id, all_states.BotStates.find_book_req_genre, call.message.chat.id)
        bot.send_message(chat_id=call.message.chat.id,
                         text=texts.write_book_genres[users_db.activeUsers[call.message.chat.id].language])
        try:
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        except ApiException:
            print("Error")
    elif call.data == "check_books":
        if len(users_db.activeUsers[call.message.chat.id].schedule) == 0:
            bot.answer_callback_query(callback_query_id=call.id, show_alert=True,
                                      text=texts.exception_schedule[users_db.activeUsers[call.message.chat.id].language])
            return
        bot.set_state(call.message.chat.id, all_states.BotStates.check_books, call.message.chat.id)
        call.data = 'move_0_0'
        checkBooks(call)
    elif call.data == "ru" or call.data == "en":
        if call.data == "ru":
            users_db.activeUsers[call.message.chat.id].language = "ru"
        elif call.data == "en":
            users_db.activeUsers[call.message.chat.id].language = "en"
        try:
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        except ApiException:
            print("Error")
        start(types.Message(message_id=call.message.message_id, from_user= bot.get_chat_member(chat_id=call.message.chat.id, user_id=call.message.chat.id).user, date=call.message.date, chat=call.message.chat, content_type=call.message.content_type, options=[], json_string=call.message.json))
    elif call.data == "download":
        try:
            output = open(f'./user_texts/{call.message.chat.id}.txt', "x")
        except FileExistsError as e:
            output = open(f'./user_texts/{call.message.chat.id}.txt', "w")
        output.write(user.getInFile(users_db.activeUsers[call.message.chat.id]))
        output.close()
        output = open(f'./user_texts/{call.message.chat.id}.txt', "rb")
        bot.send_document(chat_id=call.message.chat.id, document=output)
        output.close()


@bot.callback_query_handler(
    func=lambda call: bot.get_state(call.message.chat.id, call.from_user.id) == all_states.BotStates.check_books.name)
def checkBooks(call: telebot.types.CallbackQuery):
    call_data_local = call.data.split('_')
    act = call_data_local[0]
    output_msg = ""
    markup = types.InlineKeyboardMarkup(row_width=3)

    if act == "back":
        try:
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        except ApiException:
            print("Error")
        start(types.Message(message_id=call.message.message_id, from_user=bot.get_chat_member(chat_id=call.message.chat.id, user_id=call.message.chat.id).user, date=call.message.date, chat=call.message.chat, content_type=call.message.content_type, options=[], json_string=call.message.json))
        return
    if act == "move":
        if len(call_data_local) >= 5 and call_data_local[3] == "delete":
            users_db.activeUsers[call.message.chat.id].schedule.pop(int(call_data_local[4]))
            if len(users_db.activeUsers[call.message.chat.id].schedule) == 0:
                bot.set_state(call.message.chat.id, all_states.BotStates.start, call.message.chat.id)
                checkEssay(call)
                try:
                    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
                except ApiException:
                    print("Error")
                return
            users_db.updateSched(users_db.activeUsers[call.message.chat.id])

        number = (int(call_data_local[1]) + int(call_data_local[2])) % math.ceil(len(users_db.activeUsers[call.message.chat.id].schedule) / 5)
        to_left = types.InlineKeyboardButton('<-', callback_data=f'move_{number}_-1')
        info = types.InlineKeyboardButton(f'[{number+1}/{math.ceil(len(users_db.activeUsers[call.message.chat.id].schedule) / 5)}]', callback_data=f'-')
        to_right = types.InlineKeyboardButton('->', callback_data=f'move_{number}_1')
        markup.add(to_left, info, to_right)
        if len(call_data_local) >= 6 and call_data_local[3] + call_data_local[4] == "setread":
            users_db.activeUsers[call.message.chat.id].schedule[int(call_data_local[5])].is_read = True
            users_db.updateSched(users_db.activeUsers[call.message.chat.id])
        for i in range(number*5, min((number+1)*5, len(users_db.activeUsers[call.message.chat.id].schedule))):
            output_msg += f'{i+1}. {texts.author[users_db.activeUsers[call.message.chat.id].language]}: {users_db.activeUsers[call.message.chat.id].schedule[i].authors}. {texts.book_title[users_db.activeUsers[call.message.chat.id].language]}: {users_db.activeUsers[call.message.chat.id].schedule[i].book_name}. ' + '\n'
            if users_db.activeUsers[call.message.chat.id].schedule[i].is_read:
                delete_sched = types.InlineKeyboardButton(texts.delete_this_essay[users_db.activeUsers[call.message.chat.id].language], callback_data=f'move_{number}_0_delete_{i}')
                action = types.InlineKeyboardButton(f'{texts.check_essay[users_db.activeUsers[call.message.chat.id].language]} {i+1}', callback_data=f'checkessay_{i}')

            else:
                delete_sched = types.InlineKeyboardButton(texts.delete_this_essay[users_db.activeUsers[call.message.chat.id].language], callback_data=f'move_{number}_0_delete_{i}')
                action = types.InlineKeyboardButton(f'{texts.read_essay[users_db.activeUsers[call.message.chat.id].language]} {i+1}', callback_data=f'move_{number}_0_set_read_{i}')
            markup.add(action, delete_sched)

    if act == "checkessay":
        bot.set_state(call.message.chat.id, all_states.BotStates.check_essay, call.message.chat.id)
        checkEssay(call)
        return
    back_to_start = types.InlineKeyboardButton(texts.back[users_db.activeUsers[call.message.chat.id].language], callback_data=f'back')
    markup.add(back_to_start)
    try:
        bot.edit_message_text(message_id=call.message.message_id, reply_markup=markup, text=output_msg,
                              chat_id=call.message.chat.id)
    except ApiException:
        print("Error")

@bot.callback_query_handler(
    func=lambda call: bot.get_state(call.message.chat.id, call.from_user.id) == all_states.BotStates.check_essay.name)
def checkEssay(call: telebot.types.CallbackQuery):
    call_data_local = call.data.split('_')
    act = call_data_local[0]
    output_msg = ""
    markup = types.InlineKeyboardMarkup(row_width=3)
    if act == 'checkessay':
        if users_db.activeUsers[call.message.chat.id].schedule[int(call_data_local[1])].essay == "":
            output_msg = texts.didnt_write_essay[users_db.activeUsers[call.message.chat.id].language]
            write = types.InlineKeyboardButton(texts.write_essay[users_db.activeUsers[call.message.chat.id].language], callback_data=f'write_{call_data_local[1]}')
        else:
            output_msg = users_db.activeUsers[call.message.chat.id].schedule[int(call_data_local[1])].essay
            write = types.InlineKeyboardButton(texts.rewrite_essay[users_db.activeUsers[call.message.chat.id].language], callback_data=f'write_{call_data_local[1]}')

        markup.add(write)
        back = types.InlineKeyboardButton(texts.back[users_db.activeUsers[call.message.chat.id].language], callback_data=f'back_{call_data_local[1]}')
        markup.add(back)
        try:
            bot.edit_message_text(message_id=call.message.message_id, reply_markup=markup, text=output_msg, chat_id=call.message.chat.id)
        except ApiException:
            print("Error")

    elif call_data_local[0] == 'write':
        output_msg = f'{texts.didnt_write_essay[users_db.activeUsers[call.message.chat.id].language]}.\n{texts.delete_this_essay[users_db.activeUsers[call.message.chat.id].language]}.'
        users_db.activeUsers[call.message.chat.id].editing_essay = int(call_data_local[1])
        bot.set_state(call.message.chat.id, all_states.BotStates.write_essay, call.message.chat.id)
        try:
            bot.edit_message_text(message_id=call.message.message_id, reply_markup=markup, text=output_msg,
                                  chat_id=call.message.chat.id)
        except ApiException:
            print("Error")
    elif act == 'back':
        call.data = f'move_{math.floor(int(call_data_local[1])/5)}_0'
        bot.set_state(call.message.chat.id, all_states.BotStates.check_books, call.message.chat.id)
        checkBooks(call)

@bot.message_handler(
    func=lambda message: bot.get_state(message.chat.id,
                                       message.from_user.id) == all_states.BotStates.write_essay.name)
def edit_essay(message: telebot.types.Message):
    users_db.activeUsers[message.chat.id].schedule[users_db.activeUsers[message.chat.id].editing_essay].essay = ai_requests.check_essay(message.text).replace("*", "")
    users_db.updateSched(users_db.activeUsers[message.chat.id])
    try:
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id-1)
    except ApiException:
        print("Error")

    bot.send_message(text=texts.essay_update[users_db.activeUsers[message.chat.id].language], chat_id=message.chat.id)
    bot.set_state(message.chat.id, all_states.BotStates.start, message.chat.id)
    start(message)


@bot.message_handler(
    func=lambda message: bot.get_state(message.chat.id,
                                       message.from_user.id) == all_states.BotStates.find_book_req_genre.name)
def find_film_req_genre(message: telebot.types.Message):
    if message.text.lower() == "нет" or message.text.lower() == "no":
        users_db.activeUsers[message.chat.id].req_genre = ""
    else:
        users_db.activeUsers[message.chat.id].req_genre = message.text
    bot.send_message(chat_id=message.chat.id, text=texts.essay_update[users_db.activeUsers[message.chat.id].language])
    bot.set_state(message.chat.id, all_states.BotStates.find_fav_book, message.chat.id)


@bot.message_handler(
    func=lambda message: bot.get_state(message.chat.id,
                                       message.from_user.id) == all_states.BotStates.find_fav_book.name)
def find_fav_film(message: telebot.types.Message):
    if message.text.lower() == "нет" or message.text.lower() == "no":
        users_db.activeUsers[message.chat.id].fav_films = ""
    else:
        users_db.activeUsers[message.chat.id].fav_films = message.text
    bot.send_message(chat_id=message.chat.id,
                     text=ai_requests.film_advice(users_db.activeUsers[message.chat.id].fav_films,
                                                  users_db.activeUsers[message.chat.id].req_genre))
    bot.set_state(message.chat.id, all_states.BotStates.start, message.chat.id)


@bot.message_handler(
    func=lambda message: bot.get_state(message.chat.id,
                                       message.from_user.id) == all_states.BotStates.add_book_name.name)
def addBookName(message: telebot.types.Message):
    users_db.activeUsers[message.chat.id].schedule[
        len(users_db.activeUsers[message.chat.id].schedule) - 1].book_name = message.text
    bot.set_state(message.from_user.id, all_states.BotStates.add_author, message.chat.id)
    bot.send_message(chat_id=message.chat.id, text=texts.write_books_authors[users_db.activeUsers[message.chat.id].language])


@bot.message_handler(
    func=lambda message: bot.get_state(message.chat.id, message.from_user.id) == all_states.BotStates.add_author.name)
def addAuthors(message: telebot.types.Message):
    users_db.activeUsers[message.chat.id].schedule[
        len(users_db.activeUsers[message.chat.id].schedule) - 1].authors = message.text
    markup = types.InlineKeyboardMarkup(row_width=2)
    yes = types.InlineKeyboardButton(text=texts.yes[users_db.activeUsers[message.chat.id].language], callback_data="yes_read")
    no = types.InlineKeyboardButton(text=texts.no[users_db.activeUsers[message.chat.id].language], callback_data="no_read")
    markup.add(yes, no)
    bot.set_state(message.from_user.id, all_states.BotStates.add_read, message.chat.id)
    bot.send_message(chat_id=message.chat.id, text=texts.did_you_read[users_db.activeUsers[message.chat.id].language], reply_markup=markup)


@bot.callback_query_handler(
    func=lambda call: bot.get_state(call.message.chat.id, call.from_user.id) == all_states.BotStates.add_read.name)
def isRead(call: telebot.types.CallbackQuery):
    if call.data == "yes_read":
        users_db.activeUsers[call.message.chat.id].schedule[
            len(users_db.activeUsers[call.message.chat.id].schedule) - 1].is_read = True

        bot.set_state(call.message.chat.id, all_states.BotStates.add_essay, call.message.chat.id)
        bot.send_message(chat_id=call.message.chat.id, text= texts.write_essay_now[users_db.activeUsers[call.message.chat.id].language])
    else:
        users_db.activeUsers[call.message.chat.id].schedule[
            len(users_db.activeUsers[call.message.chat.id].schedule) - 1].is_read = False
        try:
            bot.edit_message_text(message_id=call.message.message_id, reply_markup=None, text=call.message.text,
                                  chat_id=call.message.chat.id)
        except ApiException:
            print("Error")
        bot.send_message(chat_id=call.message.chat.id, text=texts.book_added[users_db.activeUsers[call.message.chat.id].language])
        bot.set_state(call.message.chat.id, all_states.BotStates.start, call.message.chat.id)
        users_db.updateSched(users_db.activeUsers[call.message.chat.id])
        start(types.Message(message_id=call.message.message_id, from_user= bot.get_chat_member(chat_id=call.message.chat.id, user_id=call.message.chat.id).user, date=call.message.date, chat=call.message.chat, content_type=call.message.content_type, options=[], json_string=call.message.json))

@bot.message_handler(
    func=lambda message: bot.get_state(message.chat.id, message.from_user.id) == all_states.BotStates.add_essay.name)
def addEssay(message: telebot.types.Message):
    bot.set_state(message.from_user.id, all_states.BotStates.start, message.chat.id)
    users_db.activeUsers[message.chat.id].schedule[
        len(users_db.activeUsers[message.chat.id].schedule) - 1].essay = ai_requests.check_essay(message.text).replace("*", "")
    bot.send_message(text=texts.essay_update[users_db.activeUsers[message.chat.id].language], chat_id=message.chat.id)

    users_db.updateSched(users_db.activeUsers[message.chat.id])
    start(message)


bot.infinity_polling(skip_pending=True)
