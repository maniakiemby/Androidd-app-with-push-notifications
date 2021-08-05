from datetime import datetime
import sqlite3


class ConnectionDatabase:
    def __init__(self, database_name):
        self.connection = sqlite3.connect(database_name)
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()

    def create_table(self, sql: str):
        self.cursor.execute(sql)
        self.connection.commit()

    def insert_task(self, table, task, date_add=datetime.now(), date_of_performance=None, execution=0):
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
