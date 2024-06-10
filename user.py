class Schedule:
    def __init__(self, book_name: str, authors: str, essay: str = "", is_read: bool = False):
        self.__book_name = book_name
        self.__authors = authors
        self.__essay = essay
        self.__is_read = is_read

    @property
    def book_name(self):
        return self.__book_name

    @book_name.setter
    def book_name(self, value: str):
        self.__book_name = value

    @property
    def authors(self):
        return self.__authors

    @authors.setter
    def authors(self, value: str):
        self.__authors = value

    @property
    def essay(self):
        return self.__essay

    @essay.setter
    def essay(self, value: str):
        self.__essay = value

    @property
    def is_read(self):
        return  self.__is_read

    @is_read.setter
    def is_read(self, value: bool):
        self.__is_read = value

    def __str__(self):
        return f'{self.__book_name}*{self.authors}*{self.__essay}*{self.is_read}|'


class User:
    def __init__(self, tg_id: int, schedule=None, service: str = "tg", language: str = ""):

        self.__tg_id = tg_id
        if schedule is None:
            self.__schedule = []
        else:
            self.__schedule = schedule
        self.__service = service
        self.__fav_films = ""
        self.__req_genre = ""
        self.__req_country = ""
        self.__editing_essay = -1
        if language == "ru":
            self.__language = language
        else:
            self.__language = "en"

    @property
    def tg_id(self):
        return self.__tg_id

    @tg_id.setter
    def tg_id(self, value: int):
        self.__tg_id = value

    @property
    def schedule(self):
        return self.__schedule

    def add_in_schedule(self, value: Schedule):
        self.__schedule.append(value)

    def str_schedule(self):
        res = ""
        for i in self.__schedule:
            res += i
        return res

    @property
    def service(self):
        return self.__service

    @service.setter
    def service(self, value: str):
        self.__service = value

    @property
    def fav_films(self):
        return self.__fav_films

    @fav_films.setter
    def fav_films(self, value):
        self.__fav_films = value

    @property
    def language(self: str):
        return self.__language

    @language.setter
    def language(self, value: str):
        self.__language = value

    @property
    def req_genre(self):
        return self.__req_genre

    @req_genre.setter
    def req_genre(self, value: str):
        self.__req_genre = value

    @property
    def editing_essay(self):
        return self.__editing_essay

    @editing_essay.setter
    def editing_essay(self, value: int):
        self.__editing_essay = value

def parseShed(line: str):
    books = line.split("|")
    sh = []
    for book in books:
        li = book.split('*')
        if len(li) == 4:
            sh.append(Schedule(li[0], li[1], li[2], li[3] == 'True'))
    return sh

def getInFile(u: User):
    res_out = ""
    for rec in u.schedule:
        res_out += rec.book_name + "\n"
        res_out += rec.authors + "\n"*2
        res_out += rec.essay + "\n"*4
    return res_out