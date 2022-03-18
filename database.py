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
        return self.cursor.execute(f"SELECT id, task, date_of_performance FROM {table} WHERE execution = {execution};")

    def select_task(self, table, index):
        """Select all data of one item"""
        # return self.cursor.execute(f"SELECT id, task, date_add, date_of_performance FROM Tasks WHERE id={index};")
        return self.cursor.execute(f"SELECT * FROM {table} WHERE id={index};").fetchall()

    def update_task(self, table, index, task, date_of_performance):
        self.cursor.execute(f"UPDATE {table} "
                            f"SET task = '{task}', date_of_performance = '{date_of_performance}' "
                            f"WHERE id={index};")
        self.connection.commit()

    def mark_done(self, table, index):
        self.cursor.execute(f"UPDATE {table} SET execution=1 WHERE id={index};")
        self.connection.commit()

    def delete_task(self, table, index):
        self.cursor.execute(f"DELETE FROM {table} WHERE id={index};")
        self.connection.commit()


def tasks_from_db() -> dict:
    db = ConnectionDatabase()
    select = db.select_tasks('Tasks')
    task_dictionary = {}
    for index, task, date_of_performance in select:
        task_dictionary[index] = [task, date_of_performance]

    return task_dictionary


def sort_tasks_by_date(_dict: dict) -> dict:
    list_tasks = []
    for index, value in _dict.items():
        list_tasks.append((index, value[0], value[1]))

    list_tasks.sort(key=lambda val: val[2])

    _dict.clear()
    for task_group in list_tasks:
        _dict[task_group[0]] = [task_group[1], task_group[2]]

    return _dict


if __name__ == '__main__':
    task_list = tasks_from_db()
    task_dict = sort_tasks_by_date(task_list)
    print(task_dict)
