from datetime import datetime
import sqlite3


class ConnectionDb:
    def __init__(self, database_name):
        self.connection = sqlite3.connect(database_name)
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()

    def create_table(self, sql: str):
        self.cursor.execute(sql)
        self.connection.commit()

    def insert_task(self, table, task, date_add=datetime.now(), date_of_performance=None):
        self.cursor.execute(f"INSERT INTO {table} VALUES ('{task}', '{date_add}', '{date_of_performance}');")
        self.connection.commit()

    def select_tasks(self):
        return self.cursor.execute("SELECT task FROM Tasks;")

    def delete_task(self, table, task):
        self.cursor.execute(f"DELETE FROM {table} WHERE task='{task}';")
        self.connection.commit()
