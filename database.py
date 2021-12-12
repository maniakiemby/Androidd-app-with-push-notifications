from os import getenv
# from datetime import datetime
import sqlite3
from dotenv import load_dotenv


load_dotenv()


class ConnectionDatabase:
    def __init__(self, database_name=getenv('DB_NAME')):
        self.connection = sqlite3.connect(database_name)
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()

    def create_table(self, sql: str):
        self.cursor.execute(sql)
        self.connection.commit()

    def insert_task(self, table, task, date_add=None, date_of_performance=None, execution=0):
        self.cursor.execute(f"INSERT INTO {table} (task, date_add, date_of_performance, execution) "
                            f"VALUES ('{task}', '{date_add}', '{date_of_performance}', {execution});")
        self.connection.commit()

    def select_tasks(self, table, execution=0):
        """Select only 'id' and 'task' of all not complete tasks"""
        return self.cursor.execute(f"SELECT id, task FROM {table} WHERE execution = {execution};")

    def select_task(self, table, index):
        """Select all data of one item"""
        # return self.cursor.execute(f"SELECT id, task, date_add, date_of_performance FROM Tasks WHERE id={index};")
        return self.cursor.execute(f"SELECT * FROM {table} WHERE id={index};").fetchall()

    def update_task(self, table, index, task, date_of_performance):
        self.cursor.execute(f"UPDATE {table} "
                            f"SET task = {task}, date_of_performance = {date_of_performance} "
                            f"WHERE id={index};")
        self.connection.commit()

    def mark_done(self, table, index):
        self.cursor.execute(f"UPDATE {table} SET execution=1 WHERE id={index};")
        self.connection.commit()

    def delete_task(self, table, index):
        self.cursor.execute(f"DELETE FROM {table} WHERE id={index};")
        self.connection.commit()


def tasks_from_db():
    db = ConnectionDatabase()
    select = db.select_tasks('Tasks')
    tasks = []
    for index, task in select:
        tasks.append((index, task))

    return tasks


def task_from_db(task_id):
    ...
