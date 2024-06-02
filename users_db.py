import sqlite3

from sqlite3 import Error

from user import User
from user import Schedule

def createConnection(path):
    connect = None
    try:
        connect = sqlite3.connect(path)
        print("DB connected successfully")
    except Error as e:
        print(f"Error {e} occurred")

    return connect

def isExist(u: User):
    usersBase = createConnection("./data/users.sqlite")
    cursor = usersBase.cursor()
    try:
        cursor.execute(f'SELECT * FROM users WHERE tg_id = {u.tg_id}')
        for row in cursor:
            return True
        return False
    except Error as e:
        print(e)
        return False

def addUser(u: User):
    usersBase = createConnection("./data/users.sqlite")
    cursor = usersBase.cursor()
    try:
        print(f'INSERT INTO users (tg_id, schedule) VALUES({u.tg_id}, {u.str_schedule()})')
        cursor.execute(f'INSERT INTO users (tg_id, schedule, service) VALUES({u.tg_id}, \"{u.str_schedule()}\", \"{u.service}\")')
        usersBase.commit()
    except Error as e:
        print(e)
        return False

def addShed(sched: Schedule, u: User):
    pass