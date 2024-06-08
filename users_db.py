import sqlite3

from sqlite3 import Error

import user
from user import User
from user import Schedule

activeUsers = {0: User(0)}

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
            if not(row[1] in activeUsers) and len(row) == 4:
                activeUsers[row[1]] = User(row[1], user.parseShed(row[2]), row[3])
            return True
        return False
    except Error as e:
        print(e)
        return False

def addUser(u: User):
    usersBase = createConnection("./data/users.sqlite")
    cursor = usersBase.cursor()
    try:
        cursor.execute(f'INSERT INTO users (tg_id, schedule, service) VALUES({u.tg_id}, \"{u.str_schedule()}\", \"{u.service}\")')
        usersBase.commit()
    except Error as e:
        print(e)
        return False

def addShed(u: User):
    usersBase = createConnection("./data/users.sqlite")
    cursor = usersBase.cursor()
    try:
        cursor.execute(
            f'UPDATE users SET schedule = schedule || \'{u.schedule[len(u.schedule)-1]}\' WHERE tg_id = {u.tg_id}')
        usersBase.commit()
    except Error as e:
        print(e)
        return False

