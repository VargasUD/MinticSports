import sqlite3
from sqlite3 import Error

con=None #variable global para conxion
def get_db():
    try:
        con=sqlite3.connect('sport.db')
        return con
    except :
        print('Error al conectar DB..')