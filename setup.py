from sys import argv
from os import getenv

from dotenv import load_dotenv

from database import ConnectionDatabase

load_dotenv()

if len(argv) == 1:
    '''
    Initialize Database
    Usage: python setup.py
    '''
    print('Tworzę tabelę w bazie danych.')
    print(getenv('DB_NAME'))
    database = ConnectionDatabase(getenv('DB_NAME'))
    database.create_table("CREATE TABLE Tasks "
                          "(id INTEGER PRIMARY KEY AUTOINCREMENT,"
                          "task TEXT,"
                          "date_add DATETIME,"
                          "date_of_performance DATETIME,"
                          "execution BIT)"
                          )
