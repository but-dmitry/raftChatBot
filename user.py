class Schedule:
    def __init__(self, book_name: str, authors: str, esse: str = "", is_read: bool = False):
        self.__book_name = book_name
        self.__authors = authors
        self.__esse = esse
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
    def esse(self):
        return self.__esse

    @esse.setter
    def esse(self, value: str):
        self.__esse = value

    @property
    def is_read(self):
        return  self.__is_read

    @is_read.setter
    def is_read(self, value: bool):
        self.__is_read = value

    def __str__(self):
        return f'{self.__book_name}*{self.authors}*{self.__esse}*{self.is_read}|'


class User:
    def __init__(self, tg_id: int, schedule=None, service: str = "tg"):

        self.__tg_id = tg_id
        if schedule is None:
            self.__schedule = []
        else:
            self.__schedule = schedule
        self.__service = service
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

