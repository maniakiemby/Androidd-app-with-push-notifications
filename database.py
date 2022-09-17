import sqlite3


class ConnectionDatabase:
    def __init__(self):
        # self.database_name = 'database.db'
        self.database_name = 'test_database.db'
        self.connection = sqlite3.connect(self.database_name)
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()


class ConnectionDatabaseTasks(ConnectionDatabase):
    def __init__(self):
        super(ConnectionDatabaseTasks, self).__init__()
        self.table_name = 'Tasks'

    def create_table(self, sql=None):
        if not sql:
            sql = f"CREATE TABLE {self.table_name} " \
                   "(id INTEGER PRIMARY KEY AUTOINCREMENT, " \
                   "task TEXT NOT NULL, " \
                   "date_add DATETIME, " \
                   "date_of_performance DATETIME, " \
                   "execution BIT)"
        self.cursor.execute(sql)
        self.connection.commit()

    def insert_task(self, task, date_add=None, date_of_performance=None, execution=0) -> int:
        self.cursor.execute(f"INSERT INTO {self.table_name} (task, date_add, date_of_performance, execution) "
                            f"VALUES ('{task}', '{date_add}', '{date_of_performance}', {execution});")
        self.connection.commit()
        index = self.cursor.execute("SELECT last_insert_rowid();")
        return index.lastrowid

    def select_tasks(self, execution=0):
        """Select only 'id', 'task' and 'date_of_performance' of all not complete tasks"""
        return self.cursor.execute(f"SELECT id, task, date_of_performance FROM {self.table_name} "
                                   f"WHERE execution = {execution};")

    def select_task(self, index):
        """Select all data of one item"""
        # return self.cursor.execute(f"SELECT id, task, date_add, date_of_performance FROM Tasks WHERE id={index};")
        return self.cursor.execute(f"SELECT * FROM {self.table_name} WHERE id={index};").fetchall()

    def update_task(self, index, task, date_of_performance):
        self.cursor.execute(f"UPDATE {self.table_name} "
                            f"SET task = '{task}', date_of_performance = '{date_of_performance}' "
                            f"WHERE id={index};")
        self.connection.commit()

    def mark_done(self, index):
        self.cursor.execute(f"UPDATE {self.table_name} SET execution=1 WHERE id={index};")
        self.connection.commit()

    def delete_task(self, index):
        self.cursor.execute(f"DELETE FROM {self.table_name} WHERE id={index};")
        self.connection.commit()


def tasks_from_db() -> dict:
    db = ConnectionDatabaseTasks()
    select = db.select_tasks()
    task_dictionary = {}
    for index, task, date_of_performance in select:
        task_dictionary[index] = [task, date_of_performance]
    return task_dictionary


def sort_tasks_by_date(_dict: dict) -> dict:
    list_tasks = []
    list_tasks_without_date = []
    for index, value in _dict.items():
        if value[1] != 'None' and value[1] is not None:
            list_tasks.append((index, value[0], value[1]))
        else:
            list_tasks_without_date.append((index, value[0], value[1]))
    list_tasks.sort(key=lambda val: val[2])

    _dict.clear()
    for task_group in list_tasks:
        _dict[task_group[0]] = [task_group[1], task_group[2]]
    for task_group in list_tasks_without_date:
        _dict[task_group[0]] = [task_group[1], task_group[2]]

    return _dict


class ConnectionDatabaseCategoriesExpenses(ConnectionDatabase):
    def __init__(self):
        super(ConnectionDatabaseCategoriesExpenses, self).__init__()
        self.table_name = 'CategoriesOfExpenses'
        # self.values = ['paliwo',
        #                'inne wydatki na samochód',
        #                'opis, jakie wydatki na samochód',
        #                'mieszkanie / odstępne',
        #                'mieszkanie / czynsz',
        #                'abonament / telefon i internet',
        #                'inne abonamenty',
        #                'podstawowe wydatki',
        #                'niepodstawowe wydatki',
        #                'większe wydatki',
        #                'opis, jakie wydatki',
        #                'odłożone pieniądze',
        #                'Natalia dała na mieszkanie',
        #                'odsetki kart kredytowcyh i inne opłaty za prowadzenie rachunków']
        with open('categories_of_expenses.txt', 'r') as f:
            self.values = f.readlines()

    # TODO zamiast bazy danych 'kategorie' będą przechowywane w zwykłym pliku .txt

    def create_table(self, sql=None):
        if not sql:
            sql = f"CREATE TABLE IF NOT EXISTS {self.table_name} " \
                   "(id INTEGER PRIMARY KEY AUTOINCREMENT, " \
                   "category_name TEXT NOT NULL UNIQUE);"
        self.cursor.execute(sql)
        self.connection.commit()

    def create_categories(self, sql=None):
        if not sql:
            for value in self.values:
                sql = f"INSERT OR IGNORE INTO {self.table_name} (category_name) VALUES ('{value}');"
                self.cursor.execute(sql)
        self.connection.commit()


class ConnectionDatabaseExpenses(ConnectionDatabase):
    def __init__(self):
        super(ConnectionDatabaseExpenses, self).__init__()
        self.table_name = 'Expenses'

    # TODO zmienić id_category INTEGER na category TEXT (testy, metody)

    def create_table(self, sql=None):
        if not sql:
            sql = f"CREATE TABLE {self.table_name} " \
                   "(id INTEGER PRIMARY KEY AUTOINCREMENT, " \
                   "expense FLOAT, " \
                   "matter TEXT, " \
                   "id_category INTEGER, " \
                   "date_add DATETIME, " \
                   "FOREIGN KEY (id_category) REFERENCES CategoriesOfExpenses(id))"
        self.cursor.execute(sql)
        self.connection.commit()

    def insert_expense(self, expense, matter=None, category_id=None, date_add=None) -> int:
        self.cursor.execute(f"INSERT INTO {self.table_name} (expense, matter, id_category, date_add) "
                            f"VALUES ('{expense}', '{matter}', '{category_id}', '{date_add}');")
        self.connection.commit()
        index = self.cursor.execute("SELECT last_insert_rowid();")
        return index.lastrowid

    def select_expenses(self) -> dict:
        """Select all content of all unspecified expenses"""
        select = self.cursor.execute(
            f"SELECT id, expense, id_category, date_add FROM {self.table_name};").fetchall()

        task_dictionary = {}
        for index, expense, category, date_add in select:
            task_dictionary[index] = [expense, category, date_add]
        return task_dictionary

    def select_expense(self, index) -> list:
        """Select all data of one item"""
        return self.cursor.execute(
            f"SELECT * FROM {self.table_name} WHERE id={index};").fetchall()

    def update_expense(self, index, expense, matter, category_id, date_add):
        self.cursor.execute(f"UPDATE {self.table_name} "
                            f"SET expense = '{expense}',"
                            f"matter = '{matter}',"
                            f"id_category = '{category_id}',"
                            f"date_add = '{date_add}' "
                            f"WHERE id={index};")
        self.connection.commit()

    # def mark_done(self, table, index):
    #     self.cursor.execute(f"UPDATE {table} SET execution=1 WHERE id={index};")
    #     self.connection.commit()

    def delete_expense(self, index):
        self.cursor.execute(f"DELETE FROM {self.table_name} WHERE id={index};")
        self.connection.commit()


class ConnectionDatabaseExpenseData(ConnectionDatabase):
    def __init__(self):
        super(ConnectionDatabaseExpenseData, self).__init__()
        self.table_name = 'ExpenseDetails'

    def create_table(self, sql=None):  # receipt screen
        if not sql:
            sql = f"CREATE TABLE {self.table_name} " \
                  "(id INTEGER PRIMARY KEY AUTOINCREMENT, " \
                  "id_expense INTEGER NOT NULL," \
                  "category TEXT, " \
                  "date_add DATETIME, " \
                  "FOREIGN KEY (id_expense) REFERENCES Expenses(id))"
        self.cursor.execute(sql)
        self.connection.commit()


if __name__ == '__main__':
    pass
    # task_list = tasks_from_db()
    # task_dict = sort_tasks_by_date(task_list)
    # print(task_dict)
