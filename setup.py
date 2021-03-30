from sys import argv
from os import getenv

from dotenv import load_dotenv

from database import ConnectionDb

load_dotenv()

if len(argv) == 1:

    '''
    Initialize Database
    Usage: python setup.py
    '''
    print('Tworzę tabelę w bazie danych.')
    print(getenv('DB_NAME'))
    database = ConnectionDb(getenv('DB_NAME'))
    database.create_table("CREATE TABLE Tasks (task TEXT, date_add DATETIME, date_of_performance DATETIME)")
