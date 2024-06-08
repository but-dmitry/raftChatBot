from telebot.handler_backends import State, StatesGroup

class BotStates(StatesGroup):
    start = State()
    add_book_name = State()
    add_author = State()
    add_read = State()
    add_esse = State()
