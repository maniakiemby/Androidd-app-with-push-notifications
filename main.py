import os
import re
from datetime import datetime, date, time
import pdb
import time as tm
from abc import abstractmethod
from dataclasses import dataclass

import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.metrics import dp, sp
from kivy.uix.modalview import ModalView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen, ScreenManagerException, \
    FadeTransition, SlideTransition, NoTransition
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.switch import Switch
from kivy.core.window import Window
from kivy.properties import ObjectProperty
from kivy.graphics import Color

from database import ConnectionDatabaseTasks, tasks_from_db, sort_tasks_by_date, ConnectionDatabaseExpenses, \
    ConnectionDatabaseExpenseData
from modules import DatePicker, TimePicker, ExpenseLayout, TaskLayout
from my_uix import (Menu,
                    TasksPageScrollView, WrapButton, ExecuteButtonTasksView,
                    TaskButtonTasksView, ValidMessage, ErrorMessage, ValidMessageLongText, ButtonNewItem,
                    ExpensesPageScrollView, ExpenseButtonExpenseView,
                    RestoreInscription, RestoreButton, RestoreDeletedEntry
                    )

kivy.require('2.0.0')
__version__ = "0.2"


class Start(Screen):
    def __init__(self, **kwargs):
        super(Start, self).__init__(**kwargs)
        os.system('ls > file_test.txt')

        with open('file_test.txt', 'r') as f:
            if 'database.db' not in f.read():
                connection_database = ConnectionDatabaseTasks()
                connection_database.create_table()
                connection_database = ConnectionDatabaseExpenses()
                connection_database.create_table()
                connection_database = ConnectionDatabaseExpenseData()
                connection_database.create_table()
        os.system('rm file_test.txt')

    @staticmethod
    def done():
        sm.transition.direction = 'down'
        sm.current = 'tasks'


def back(transition=None, direction='right', current='start', *args):
    """ This function is used to move between screens.
    Argument 'transition' is used for transition direction effect.
    Argument 'direction' can be 'left', 'right', 'up' or 'down'.
    Argument 'current' must contains name of screen that we going.
    """

    if transition:
        if transition == 'no_transition':
            sm.transition = NoTransition()
    if direction:
        sm.transition.direction = direction
    if current:
        sm.current = current
    if transition:
        sm.transition = SlideTransition()


class TaskBoard(GridLayout):
    def __init__(self, **kwargs):
        super(TaskBoard, self).__init__(**kwargs)
        self.bind(minimum_height=self.setter('height'))
        self.restoring_task = {}
        self.all_tasks = sort_tasks_by_date(tasks_from_db())
        self.display_gui()

    def display_gui(self):
        for index, task in self.all_tasks.items():
            self.add_task_to_gui(index=index, task=task)

    def add_task_to_gui(self, index, task):
        if isinstance(task[0], RestoreDeletedEntry):
            button_execute = BoxLayout(size_hint=(None, None), size=(0, 0))
            button_named = RestoreInscription(on_release=self.restore, index=index, info='content')
        else:
            button_execute = ExecuteButtonTasksView(
                on_release=self.complete, index=index, info='execute')
            button_named = TaskButtonTasksView(
                text=task[0], on_release=self.doorway, index=index, info='content')
        self.add_widget(button_execute)
        self.add_widget(button_named)

    def add_new_task_to_gui(self, index, essence, date_of_performance):
        self.all_tasks[index] = [essence, date_of_performance]
        self.sort_tasks()

    def sort_tasks(self):
        self.clear_widgets()
        self.all_tasks = sort_tasks_by_date(self.all_tasks)
        self.display_gui()

    def find_layout_task_in_grid(self, index: int) -> tuple:
        result = []
        for obj in self.walk():
            if isinstance(obj, WrapButton):
                if obj.index == index:
                    result.append(obj)

        return tuple(result)

    def del_task_from_gui(self, index: int):
        task_layout = self.find_layout_task_in_grid(index=index)
        for obj in task_layout:
            self.remove_widget(obj)
        self.all_tasks.pop(index)

    def doorway(self, *instance):
        instance_id = instance[0].index
        task_window_gui = sm.get_screen('task_window')
        task_window_gui.receive_content(instance_id)
        back(direction='left', current='task_window')
        if len(self.restoring_task) > 0:
            self.mark_done()

    def complete(self, *instance):
        instance_id = instance[0].index
        self.display_recovery_message(index=instance_id)

    def display_recovery_message(self, index):
        restore_statement = RestoreDeletedEntry(index=index)
        self.restoring_task[index] = self.all_tasks[index]
        self.all_tasks[index] = [restore_statement, None]
        self.sort_tasks()

    def restore(self, *args):
        index = list(self.restoring_task.keys())[0]
        self.all_tasks[index] = self.restoring_task[index]
        self.restoring_task.pop(index)
        self.sort_tasks()

    def mark_done(self):
        indexes = list(self.restoring_task.keys())
        db = ConnectionDatabaseTasks()
        for index in indexes:
            db.mark_done(index)
            self.del_task_from_gui(index)
            self.restoring_task.pop(index)


class ToDoTasksPage(Screen):
    def __init__(self, **kwargs):
        super(ToDoTasksPage, self).__init__(**kwargs)
        self.menu = Menu(current='tasks')
        self.menu.menu_action_bar.action_button.bind(on_press=self.switch_to_expenses_page)

        self.button_adding_new_task = ButtonNewItem()
        self.button_adding_new_task.bind(on_press=self.switch_to_add_task_screen)

        self.scroll_view = TasksPageScrollView()
        self.task_board = TaskBoard()
        self.scroll_view.add_widget(self.task_board)

        self.add_widget(self.menu)
        self.add_widget(self.scroll_view)
        self.add_widget(self.button_adding_new_task)

    @staticmethod
    def switch_to_add_task_screen(*args):
        back(transition='no_transition', current='add_task')

    @staticmethod
    def switch_to_expenses_page(*args):
        back(direction='up', current='expenses')


@dataclass
class Task:
    def __init__(self):
        self.task_id = int
        self.task_content = str
        self.task_date_add = datetime.now().isoformat(sep=' ', timespec='seconds')
        self.task_date_of_performance = str  # DD/MM/RRRR GG:MM

        self.task_date = None  # Must be datetime object
        self.task_time = None  # too

        self.background_color = str
        self.font_color = str

    def valid_content(self):
        len_task_content = len(self.task_content)
        if len_task_content == 0 or len_task_content > 300:
            popup = ErrorMessage()
            popup.message_content.text = "Tekst jest zbyt rozległy, dopuszczalna ilość znaków to 300"
            return False
        elif len_task_content < 300:
            return True

    def merge_date(self):
        if self.task_time:
            if self.task_date:
                self.task_date_of_performance = '{} {}'.format(
                    self.task_date, self.task_time
                )
            else:
                self.task_date_of_performance = '{} {}'.format(
                    datetime.now().date().isoformat(), self.task_time
                )
        else:
            self.task_date_of_performance = '{}'.format(
                self.task_date
            )


@dataclass
class ExistingTask(Task):
    # def __init__(self):
    #     super(ExistingTask, self).__init__()

    def receive_content(self):
        db = ConnectionDatabaseTasks()
        task = db.select_task(self.task_id)
        self.task_content = task[0][1]
        self.task_date_add = task[0][2]
        self.task_date_of_performance = task[0][3]
        if self.task_date_of_performance != 'None':
            values = self.task_date_of_performance.split(sep=' ', maxsplit=1)
            self.task_date = date.fromisoformat(values[0])
            if len(values) == 2:
                self.task_time = time.fromisoformat(values[1])

    def update_data(self):
        self.merge_date()
        db = ConnectionDatabaseTasks()
        try:
            db.update_task(index=self.task_id,
                           task=self.task_content,
                           date_of_performance=self.task_date_of_performance)
        except ValueError:
            # TODO  dodać jakiś komunikat `print`ujący do konsoli ten błąd
            return False
        return True


@dataclass
class NewTask(Task):
    def __init__(self, content_input):
        super().__init__()
        self.input = content_input

    def parse_input(self):
        self.input = self.input.strip()
        self.input = self.input.replace('\'', '\"')

        self.search_date_of_performance_in_input()
        self.search_time_of_performance_in_input()
        self.merge_date()

        self.task_content = self.input

    def search_date_of_performance_in_input(self):
        if not self.task_date:
            months = {'01': ['sty', 'jan'],
                      '02': ['lut', 'feb'],
                      '03': ['mar'],
                      '04': ['kwi', 'apr'],
                      '05': ['maj', 'may'],
                      '06': ['cze', 'jun'],
                      '07': ['lip', 'jul'],
                      '08': ['sie', 'aug'],
                      '09': ['wrz', 'sep'],
                      '10': ['paz', 'paź', 'oct'],
                      '11': ['lis', 'nov'],
                      '12': ['gru', 'dec']}

            regex_search_date = re.compile('(\s|^)\d{1,2}\s*\w{3}(\s|$)|(\s|^)\w{3}\s*\d{1,2}(\s|$)|$')
            found_date = re.search(regex_search_date, self.input).group()
            found_date = found_date.lower()
            if found_date:
                month = re.sub('\d*\s*', '', found_date)
                months_names = []
                [months_names.extend(name) for name in months.values()]
                if month in months_names:
                    day = re.search('\d*', found_date).group(0)
                    if len(day) == 1:
                        day = '0' + day
                    month_num = None
                    for key, values in months.items():
                        for word in values:
                            if month == word:
                                month_num = key
                                break
                    _date = '{year}-{month}-{day}'.format(year=date.today().year, month=month_num, day=day)
                    try:
                        self.task_date = date.fromisoformat(_date)
                    except ValueError:
                        'day is out of range for month'
                    else:
                        self.task_content = re.sub(regex_search_date, ' ', self.input)
                        if self.task_date < date.today():
                            self.task_date = self.task_date.replace(year=date.today().year + 1)

    def search_time_of_performance_in_input(self):
        if not self.task_time:
            regex_search_time = re.compile('(\s|^)\d{2}:\d{2}(\s|$)|(\s|^)\d:\d{2}(\s|$)|$')
            found_time = re.search(regex_search_time, self.input).group()
            found_time = found_time.strip()
            if found_time:
                if len(found_time) == 4:
                    found_time = '0' + found_time
                try:
                    self.task_time = time.fromisoformat(found_time)
                except ValueError:
                    'time is not correctly !'
                else:
                    self.task_content = re.sub(regex_search_time, '', self.input)


class AddTaskPage(Screen, TaskLayout):
    def __init__(self, **kwargs):
        super(AddTaskPage, self).__init__(**kwargs)
        self.task = None

    def on_confirm(self):
        content_input = self.content_input.text
        self.task = NewTask(content_input)
        self.task.task_date = self.task_date_of_performance.text
        self.task.task_time = self.task_time_of_performance.text
        # self.task.background_color = self.button_change_background_color.text
        # self.task.font_color = self.button_change_font_color.text

        self.task.parse_input()

        if self.task.valid_content():
            index = self.insert()
            self.clear_the_fields()
            page = sm.get_screen('tasks')
            page.task_board.add_new_task_to_gui(
                index, self.new_task.task_content, self.new_task.task_date_of_performance
            )

    def insert(self, *args):
        db = ConnectionDatabaseTasks()
        index = db.insert_task(task=self.new_task.task_content,
                               date_add=self.new_task.task_date_add,
                               date_of_performance=self.new_task.task_date_of_performance)
        return index

    @staticmethod
    def back(*args):
        back(direction='right', current='tasks')


class TaskWindow(Screen, TaskLayout):
    def __init__(self, **kwargs):
        super(TaskWindow, self).__init__(**kwargs)
        self.task = None

    def receive_content(self, index):
        self.task = ExistingTask()
        self.task.task_id = index
        self.task.receive_content()
        self.layout.content_input.text = self.task.task_content
        if self.task.task_date:
            self.layout.task_date_of_performance.text = self.task.task_date.isoformat()
        if self.task.task_time:
            self.layout.task_time_of_performance.text = self.task.task_time.isoformat(timespec='minutes')
        if self.task.background_color:
            pass
        if self.task.font_color:
            pass

    def on_confirm(self, *args):
        if self.fields_filled():
            if self.task.valid_content():
                self.task.update_data()

    @staticmethod
    def back(*args):
        back(direction='right', current='tasks')


# Below for application Notebook


class ExpensesNotebook(GridLayout):
    def __init__(self, **kwargs):
        super(ExpensesNotebook, self).__init__(**kwargs)
        self.bind(minimum_height=self.setter('height'))
        self.index = 0  # It is for self.walk() method
        self.cached_expenses = {}
        db = ConnectionDatabaseExpenses()
        self.all_expenses = db.select_expenses()  # all_expenses[index] = [expense, category, date_add]
        self.display_gui()

    def display_gui(self):
        for key in self.all_expenses.keys():
            expense = self.all_expenses[key]  # list of expense items from the dictionary
            self.add_expense_to_gui(expense_id=key, expense=expense[0], category=expense[1])

    def add_new_expense(self, expense_id, expense, category, date_add):
        self.all_expenses[expense_id] = [expense, category, date_add]
        self.add_expense_to_gui(expense_id, expense, category)

    def add_expense_to_gui(self, expense_id, expense, category):
        expense = str(expense).replace('.', ',')
        if ',' not in expense:
            expense = expense + ',0'
        wrap_button = ExpenseButtonExpenseView(
            text="{:<11} {}".format(expense, category),
            on_release=self.doorway,
            index=expense_id,
            info='content'
        )
        self.add_widget(wrap_button)

    def refresh_gui(self):
        self.clear_widgets()
        # TODO mogę jeszcze dodać sortowanie po dacie dodania, o ile nie są w ten sposób dodawane zadania.
        self.display_gui()

    def doorway(self, *args):
        index = args[0].index  # index of current expense
        info = args[0].info
        if info == 'cache':
            self.restore(index=index)
        else:
            self.make_the_removal()
            window = sm.get_screen(name='expense_window')
            window.receive_content(index_expense=index)
            back(direction='left', current='expense_window')

    def update_row(self, index: int, expense: str, category: str):
        for row in self.walk():
            if isinstance(row, ExpenseButtonExpenseView):
                if row.index == index:
                    expense = str(expense).replace('.', ',')
                    row.text = "{:<11} {}".format(expense, category)
                    row.info = 'content'

    def remove_expense(self, index):
        expense = self.all_expenses[index]
        self.cached_expenses[index] = expense
        self.display_recovery_message(index=index)

    def display_recovery_message(self, index):
        for row in self.walk(restrict=True):
            if row.index == index:
                row.text = "{}".format('Naciśnij aby przywrócić usuwany element')
                row.info = 'cache'
                return

    def restore(self, index):
        expense = self.all_expenses[index]
        self.update_row(index=index, expense=expense[0], category=expense[1])
        self.cached_expenses.pop(index)

    def make_the_removal(self):
        if len(self.cached_expenses) > 0:
            indexes = list(self.cached_expenses.keys())
            for row in self.walk(restrict=True):
                index = row.index
                if index in indexes:
                    self.cached_expenses.pop(index)
                    self.remove_widget(row)
                    db = ConnectionDatabaseExpenses()
                    db.delete_expense(index)


class ExpensesPage(Screen):
    def __init__(self, **kwargs):
        super(ExpensesPage, self).__init__(**kwargs)
        self.menu = Menu(current='notebook')
        self.menu.menu_action_bar.action_button.bind(on_press=self.switch_to_todo_tasks_page)
        self.add_widget(self.menu)

        self.expenses = ExpensesNotebook()
        self.scroll_view = ExpensesPageScrollView()
        self.scroll_view.add_widget(self.expenses)
        self.add_widget(self.scroll_view)

        self.button_new_expense = ButtonNewItem()
        self.button_new_expense.bind(on_press=self.switch_to_add_expense_page)
        self.add_widget(self.button_new_expense)

    def switch_to_todo_tasks_page(self, *args):
        back(direction='down', current='tasks')
        self.expenses.make_the_removal()

    def switch_to_add_expense_page(self, *args):
        back(transition='no_transition', current='add_expense')
        self.expenses.make_the_removal()

    # TODO link do XAMPP czyli narzędzia budującego lokalny host na komputerze.
    #  https://stackoverflow.com/questions/42704846/running-python-scripts-with-xampp
    #  https://blog.terresquall.com/2021/10/running-python-in-xampp/


class Expense:
    def __init__(self):
        self.current_id = None
        self.expense = ''
        self.category = ''
        self.matter = ''
        self.date_add = ''

    def receive_content(self, index_expense):
        self.current_id = index_expense
        self.fetch_data_from_db()

    def fetch_data_from_db(self):
        db = ConnectionDatabaseExpenses()
        select = db.select_expense(self.current_id)
        try:
            self.expense = str(select[0][1])
            self.expense = self.expense.replace('.', ',')
            self.category = select[0][2]
            self.matter = select[0][3]
            self.date_add = select[0][4]
        except IndexError:
            "list index out of range"
            "it looks select -> {}".format(select)

    def update_expense_in_db(self):
        db = ConnectionDatabaseExpenses()
        db.update_expense(index=self.current_id,
                          expense=self.expense,
                          category=self.category,
                          matter=self.matter,
                          date_add=self.date_add)


class AddExpensePage(Screen, ExpenseLayout):
    def __init__(self, **kwargs):
        super(AddExpensePage, self).__init__(**kwargs)
        # self.button_cancel.bind(on_release=self.back)
        # self.button_confirm.bind(on_release=self.insert_expense)
        self.matter_field.bind(on_text_validate=self.insert_expense)
        self.expense_field.bind(on_text_validate=self.insert_expense)

    def insert_expense(self, *args):
        if self.data_complete():
            if self.amount_money_correctly():
                expense_index = self.insert()
                gui = sm.get_screen('expenses').expenses
                gui.add_new_expense(expense_index,
                                    self.expense_field.text,
                                    self.category_selector.text,
                                    self.date_add)
                self.clear_the_fields()

    def insert(self):
        db = ConnectionDatabaseExpenses()
        # todo obsłużyć, gdyby nie udało się jednak dodać wpisu.
        returned_id = db.insert_expense(expense=self.expense_field.text,
                                        category=self.category_selector.text,
                                        matter=self.matter_field.text,
                                        date_add=self.date_add)
        return returned_id

    def back(self, *args):
        back(transition='no_transition', current='expenses')
        self.clear_the_fields()


class ExpenseWindow(Screen, ExpenseLayout):
    def __init__(self, **kwargs):
        super(ExpenseWindow, self).__init__(**kwargs)
        # self.button_cancel.bind(on_release=self.back)
        # self.button_confirm.bind(on_release=self.confirm)
        self.button_remove_expense = self.ids['remove']
        self.button_remove_expense.bind(on_release=self.remove)
        self.expense = Expense()

    def receive_content(self, index_expense):
        self.expense.receive_content(index_expense=index_expense)
        self.expense_field.text = self.expense.expense
        self.category_selector.text = self.expense.category
        self.matter_field.text = self.expense.matter
        self.button_date_add.text = self.expense.date_add

    def confirm(self, *args):
        if self.data_complete():
            if self.amount_money_correctly():
                self.fetch_data_from_fields()
                self.expense.update_expense_in_db()
                gui = sm.get_screen('expenses').expenses
                gui.update_row(index=self.expense.current_id,
                               expense=self.expense.expense,
                               category=self.expense.category)
                self.back()
                self.clear_the_fields()

    def fetch_data_from_fields(self):
        self.expense.expense = self.expense_field.text
        self.expense.category = self.category_selector.text
        self.expense.matter = self.matter_field.text
        self.expense.date_add = self.button_date_add.text

    def remove(self, *args):
        gui = sm.get_screen('expenses').expenses
        gui.remove_expense(self.expense.current_id)
        self.back()

    def back(self, *args):
        back(direction='right', current='expenses')
        self.clear_the_fields()


class WindowManager(ScreenManager):
    pass


Builder.load_file("MyApp.kv")

sm = WindowManager()

screens = [Start(name='start'), ToDoTasksPage(name='tasks'), AddTaskPage(name='add_task'),
           TaskWindow(name='task_window'), ExpensesPage(name='expenses'), AddExpensePage(name='add_expense'),
           ExpenseWindow(name='expense_window')]
for screen in screens:
    sm.add_widget(screen)

sm.current = 'start'
Start.done()


class MyApp(App):
    def build(self):
        Window.clearcolor = (151 / 255, 152 / 255, 164 / 255)
        # Window.clearcolor = (.85, .9, .85, .3)
        return sm


if __name__ == '__main__':
    MyApp().run()
    # do wyłączania aplikacji App.get_running_app().stop()
    # https://stackoverflow.com/questions/62498639/python-kivy-how-to-optimize-screen-resolution-for-all-devices
    # python main.py --size=1440x2960 --dpi=529
