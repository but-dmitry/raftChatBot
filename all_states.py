from telebot.handler_backends import State, StatesGroup

class BotStates(StatesGroup):
    start = State()

    add_book_name = State()
    add_author = State()
    add_read = State()
    add_essay = State()

    find_fav_book = State()
    find_book_req_genre = State()

    check_books = State()
    check_essay = State()

    write_essay = State()
