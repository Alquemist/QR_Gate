import random
import string
import sqlite3
from datetime import datetime, timedelta
from time import sleep

conn = sqlite3.connect('QRs.db')
c = conn.cursor()


with conn:
    c.execute('''CREATE TABLE IF NOT EXISTS codes (code text, valid bool, expires_at datetime, used bool, id integer primary key autoincrement)''')


def get_random_string(length):
    letters = string.ascii_lowercase
    random_str = ''.join(random.choice(letters) for i in range(length))
    return(random_str)


def getNewCode(length):
    conn = sqlite3.connect('QRs.db')
    c = conn.cursor()
    code = get_random_string(length)
    newCode = {
        'code': code, 
        'valid': True,
        'expires_at': '',
        'used': False
        }
    with conn:
        try:
            c.execute("INSERT INTO codes VALUES (?,?,?,?,?)", (newCode['code'], True, '', False, None))
        except Exception as err:
            print(err.args)
            return err.args
        id = c.lastrowid
    return {'id': id, 'code': newCode['code']}


def updAndGetNew(id, length, expiresAfter):
    conn = sqlite3.connect('QRs.db')
    c = conn.cursor()
    code = get_random_string(length)
    newCode = {
        'code': code, 
        'valid': True,
        'expires_at': '',
        'used': False
        }
    with conn:
        #expires_at = datetime.now() + timedelta(hours=expiresAfter)
        #print("UPDATE codes set expires_at = '{}', WHERE id = {}".format(expires_at.strftime("%Y-%m-%d, %H:%M:%S"), id))
        try:
            c.execute("UPDATE codes set expires_at = datetime('now', 'localtime', '+{} hours') WHERE id = {}".format(expiresAfter, id))
            c.execute("INSERT INTO codes VALUES (?,?,?,?,?)", (newCode['code'], True, '', False, None))
            id = c.lastrowid
            return {'id': id, 'code': newCode['code']}
        except Exception as err:
            print(err.args)
            return err.args
    


def dbCleaner():
    conn = sqlite3.connect('QRs.db')
    c = conn.cursor()
    while True:
        with conn:
            try:
                c.execute("DELETE FROM codes where expires_at < datetime('now', 'localtime') AND NOT expires_at = '' ")
                conn.commit()
            except Exception as err:
                print(err)
    sleep(600)


def doesCodeExists(code):
    conn = sqlite3.connect('QRs.db')
    c = conn.cursor()
    #print("UPDATE codes set used = 'True' WHERE code = {}".format(code))
    with conn:
        c.execute("UPDATE codes set used = 'True' WHERE code = '{}'".format(code))
        #print('rowcount: ',c.rowcount)
    return True if c.rowcount else False