import os
import re
from datetime import datetime, date, time
import pdb

import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.modalview import ModalView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen, ScreenManagerException, \
    FadeTransition, SlideTransition, NoTransition
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.properties import ObjectProperty
from kivy.graphics import Color

from database import ConnectionDatabaseTasks, tasks_from_db, sort_tasks_by_date, ConnectionDatabaseExpenses, \
    ConnectionDatabaseExpenseData
from modules import DatePicker, TimePicker, Content, ExpenseLayout
from my_uix import (Menu,
                    TasksPageScrollView, WrapButton, ExecuteButtonTasksView,
                    TaskButtonTasksView, ValidMessage, ErrorMessage, ValidMessageLongText, ButtonNewTask,
                    ExpensesPageScrollView, ExpenseButtonExpenseView,
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

        self.all_tasks = sort_tasks_by_date(tasks_from_db())

        for index, task in self.all_tasks.items():
            # self.layout = TaskGridLayoutTaskBoard(date_of_performance=task[1])
            self.button_execute = ExecuteButtonTasksView(on_release=self.execute, index=index, info='execute')
            self.add_widget(self.button_execute)

            self.button_named = TaskButtonTasksView(text=task[0], on_release=self.doorway, index=index, info='content')
            self.add_widget(self.button_named)
            # self.add_widget(self.layout)

    def add_new_task_to_gui(self, index, essence, date_of_performance):
        self.all_tasks[index] = [essence, date_of_performance]
        self.sort_tasks()

    def sort_tasks(self):
        self.clear_widgets()
        self.all_tasks = sort_tasks_by_date(self.all_tasks)
        for index, task in self.all_tasks.items():
            self.button_execute = ExecuteButtonTasksView(on_release=self.execute, index=index, info='execute')
            self.add_widget(self.button_execute)

            self.button_named = TaskButtonTasksView(text=task[0], on_release=self.doorway, index=index, info='content')
            self.add_widget(self.button_named)

    def del_task_from_gui(self, index):
        for obj in self.walk():
            if isinstance(obj, WrapButton):
                if obj.index == index:
                    self.remove_widget(obj)
        self.all_tasks.pop(index)

    @staticmethod
    def doorway(*instance):
        instance_id = instance[0].index
        MainWindow.current_id = instance_id
        back(direction='left', current='task_window')
        # sm.transition.direction = 'left'
        # sm.current = 'task_window'

    def execute(self, *instance):
        instance_id = instance[0].index
        db = ConnectionDatabaseTasks()
        db.mark_done(instance_id)
        self.del_task_from_gui(instance_id)


class ToDoTasksPage(Screen):
    def __init__(self, **kwargs):
        super(ToDoTasksPage, self).__init__(**kwargs)
        self.menu = Menu(current='tasks')
        self.menu.menu_action_bar.action_button.bind(on_press=self.switch_to_expenses_page)

        self.button_adding_new_task = ButtonNewTask()
        self.button_adding_new_task.bind(on_press=self.switch_to_add_task_screen)

        self.scroll_view = TasksPageScrollView()
        self.scroll_view.button_new_task_obj = self.button_adding_new_task
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


class Task:
    def __init__(self, task_id):
        self.task_id = task_id
        self.task_content = None
        self.task_date_add = None
        self.task_date_of_performance = None

        self.task_date = None  # Must be datetime object
        self.task_time = None  # too

    @property
    def task_content(self):
        return self.__task_content

    @task_content.setter
    def task_content(self, value):
        if value is not None:
            self.__task_content = value.strip()

    def receiving_content(self):
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


class AddTaskPage(Screen):
    def __init__(self, **kwargs):
        super(AddTaskPage, self).__init__(**kwargs)
        self.content = Content(behavior='new data')
        self.content.text_input.is_focusable = True
        self.content.text_input.bind(on_text_validate=self.grab_content_of_new_task)  # event 'on_enter'
        self.content.confirm_adding.bind(on_press=self.grab_content_of_new_task)
        self.content.cancel_button.bind(on_press=self.cancel)
        self.ids['layout'].add_widget(self.content)
        self.new_task = None

    def grab_content_of_new_task(self, *args):
        _input_content = None
        _input_content = self.content.text_input.text

        if _input_content:
            self.new_task = NewTask(_input_content)
            # pdb.set_trace()
            if self.new_task.task_content == 'long':
                popup = ValidMessageLongText()
                popup.open()

            elif self.new_task.task_content and self.new_task.task_content != 'long':
                self.new_task.search_date_of_performance()
                if self.new_task.task_content == 'long':
                    popup = ValidMessageLongText()
                    popup.open()
                    return
                elif self.new_task.task_date_of_performance:
                    if self.new_task.task_date_of_performance < self.new_task.task_date_add:
                        self.change_year()
                        # popup = ValidMessageChangeYear()
                        # popup.confirm.bind(on_press=self.change_year)
                        # popup.cancel.bind(on_press=self.insert)
                        # popup.open()
                self.insert()

    def change_year(self, *args):
        self.new_task.task_date_of_performance = datetime.fromisoformat(self.new_task.task_date_of_performance)
        self.new_task.task_date_of_performance = self.new_task.task_date_of_performance.replace(
            year=date.today().year + 1
        ).isoformat(sep=' ', timespec='minutes')

    def insert(self, *args):
        db = ConnectionDatabaseTasks()
        index = db.insert_task(task=self.new_task.task_content,
                               date_add=self.new_task.task_date_add,
                               date_of_performance=self.new_task.task_date_of_performance)
        self.content.text_input.text = ''
        # self.content.text_input.focus = True
        page = sm.get_screen('tasks')
        page.task_board.add_new_task_to_gui(index, self.new_task.task_content, self.new_task.task_date_of_performance)

    @staticmethod
    def cancel(*args):
        back(transition='no_transition', current='tasks')


class NewTask:
    def __init__(self, all_content):
        self.table_name = 'Tasks'
        self.input_task = all_content
        self.task_date_add = '{} {}'.format(datetime.now().date().isoformat(),
                                            datetime.now().time().isoformat(timespec='seconds'))
        self.task_date_of_performance = None
        # self.search_date_of_performance()
        self.task_content = self.input_task

    def search_date_of_performance(self):
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

        regex_search_date = '(\s|^)\d{1,2}\s*\w{3}(\s|$)|(\s|^)\w{3}\s*\d{1,2}(\s|$)'
        search_date = re.search(regex_search_date, self.input_task)
        if search_date:
            found_date = search_date.group(0).strip().lower()
            self.input_task = re.sub(regex_search_date, ' ', self.input_task)

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
                found_date = '{year}-{month}-{day}'.format(year=date.today().year, month=month_num, day=day)
                try:
                    date.fromisoformat(found_date)
                except ValueError:
                    'day is out of range for month'
                    found_date = None
            else:
                search_date = None

        regex_search_time = '(\s|^)\d{2}:\d{2}(\s|$)|(\s|^)\d:\d{2}(\s|$)'
        search_time = re.search(regex_search_time, self.input_task)
        found_time = None
        if search_time:
            found_time = search_time.group(0).strip()
            if len(found_time) == 4:
                found_time = '0' + found_time
            try:
                try_datetime = '{} {}'.format(datetime.now().date().isoformat(), found_time)
                datetime.fromisoformat(try_datetime)
            except ValueError:
                'time is not correctly !'
                found_time = None
            else:
                self.input_task = re.sub(regex_search_time, '', self.input_task)

        if search_date:
            if found_time:
                self.task_date_of_performance = '{date} {time}'.format(date=found_date, time=found_time)
            else:
                self.task_date_of_performance = found_date
        else:
            if found_time:
                self.task_date_of_performance = '{date} {time}'.format(
                    date=date.today().isoformat(), time=found_time
                )

        if len(self.input_task) > 300:
            self.task_content = 'long'
        else:
            self.task_content = self.input_task

        # print(self.task_content)
        # print(self.input_task)

    @property
    def task_content(self):
        return self.__task_content

    @task_content.setter
    def task_content(self, value):
        value = value.strip()
        if len(value) == 0:
            self.__task_content = False
        elif len(value) > 330:
            self.__task_content = 'long'
        else:
            self.__task_content = value


class MainWindow(Screen):
    current_id = None
    task_content = ObjectProperty(None)
    task_date_of_performance = ObjectProperty(None)
    task_time_of_performance = ObjectProperty(None)
    task = Task(current_id)

    def button_back(self):
        self.grab_content()
        result = self.task.update_data()
        gui = sm.get_screen('tasks').task_board
        gui.all_tasks[self.task.task_id] = [self.task.task_content, self.task.task_date_of_performance]
        gui.sort_tasks()
        back(direction='right', current='tasks')
        if not result:
            ErrorMessage()

    def on_enter(self, *args):
        self.task = Task(self.current_id)
        self.task.receiving_content()
        self.task_content.text = self.task.task_content
        if self.task.task_date:
            self.task_date_of_performance.text = self.task.task_date.isoformat()
        else:
            self.task_date_of_performance.text = 'Dodaj datę'
        if self.task.task_time:
            self.task_time_of_performance.text = self.task.task_time.isoformat(timespec='minutes')
        else:
            self.task_time_of_performance.text = 'Dodaj czas'

    def execute(self, *args):
        db = ConnectionDatabaseTasks()
        db.mark_done(index=self.current_id)
        sm.get_screen('tasks').task_board.del_task_from_gui(self.task.task_id)
        back(direction='right', current='tasks')

    def change_date_of_performance(self, *args):
        if self.task.task_date is not None:
            date_picker = DatePicker(self.task.task_date)
        else:
            date_picker = DatePicker()

        app = App.get_running_app()
        app.popup = ModalView(size_hint=(None, None),
                              size=(Window.width - 25, Window.height / 1.7),
                              auto_dismiss=True,
                              on_dismiss=self.grab_date
                              )
        app.popup.add_widget(date_picker)
        app.save_data = True
        app.popup.open()

    def grab_date(self, *args):
        app = App.get_running_app()
        if app.save_data:
            _input_date = None
            for arg in args[0].walk(restrict=True):
                if isinstance(arg, Label):
                    _input_date = arg.text
                    break

            _input_date = [num for num in _input_date.split('/')]
            _input_date.reverse()
            _input_date = '-'.join(_input_date)
            _input_date = date.fromisoformat(_input_date)

            self.task.task_date = _input_date

            for gui in self.walk(restrict=True):
                if isinstance(gui, Button):
                    if re.search('\d*-\d*-\d*', gui.text) or gui.text.startswith('Dodaj datę'):
                        gui.text = self.task.task_date.isoformat()

    def change_time_of_performance(self, *args):
        if self.task.task_time is not None:
            time_picker = TimePicker(self.task.task_time)
        else:
            time_picker = TimePicker()
        app = App.get_running_app()
        app.popup = ModalView(size_hint=(None, None),
                              pos_hint={'top': .9},
                              size=(Window.width / 1.5, Window.height / 3),
                              auto_dismiss=True,
                              on_dismiss=self.grab_time
                              )
        app.popup.add_widget(time_picker)
        app.save_data = True
        app.popup.open()

    def grab_time(self, *args):
        app = App.get_running_app()
        if app.save_data:
            _input_time = []
            for arg in args[0].walk(restrict=True):
                if isinstance(arg, TextInput):
                    if arg.text == '':
                        if len(_input_time) > 0:
                            break
                        _input_time = None
                        break
                    elif len(arg.text) == 2:
                        _input_time.append(arg.text)
                    elif len(arg.text) == 1:
                        _input_time.append('0' + arg.text)
            if _input_time is not None:
                if len(_input_time) == 1:
                    _input_time = '{}:00'.format(_input_time[0])
                elif len(_input_time) == 2:
                    _input_time = ':'.join(_input_time)
                try:
                    self.task.task_time = time.fromisoformat(_input_time)
                    for gui in self.walk(restrict=True):
                        if isinstance(gui, Button):
                            if re.search('\d{2}:\d{2}', gui.text) or gui.text.startswith('Dodaj czas'):
                                gui.text = self.task.task_time.isoformat(timespec='minutes')
                except ValueError:
                    "Possibly incorrect data was entered."
                    popup = ErrorMessage()
                    popup.message_content.text = "Wprowadź poprawną godzinę\nw formacie 24h:60m"

    def grab_content(self):
        for arg in self.walk():
            if isinstance(arg, TextInput):
                updated_task_content = arg.text
                if updated_task_content != '':
                    self.task.task_content = updated_task_content
                break


class ExpensesNotebook(GridLayout):
    def __init__(self, **kwargs):
        super(ExpensesNotebook, self).__init__(**kwargs)
        self.bind(minimum_height=self.setter('height'))

        db = ConnectionDatabaseExpenses()
        self.all_expenses = db.select_expenses()

        for key in self.all_expenses.keys():
            expense = self.all_expenses[key]  # list of expense items from the dictionary
            self.add_expense_to_gui(expense_id=key, expense=expense[0], category=expense[1])

    def add_expense_to_gui(self, expense_id, expense, category):
        expense = str(expense).replace('.', ',')
        if ',' not in expense:
            expense = expense + ',0'
        wrap_button = ExpenseButtonExpenseView(
            text="{:<11} {}".format(expense, category),
            on_release=self.doorway, index=expense_id, info='content'
        )
        self.add_widget(wrap_button)

    @staticmethod
    def doorway(*args):
        index = args[0].index  # index of our expense
        window = sm.get_screen(name='expense_window')
        window.receive_content(index_expense=index)
        back(direction='left', current='expense_window')

    def update_row(self, index: int, expense: str, category: str):
        for row in self.walk():
            if isinstance(row, ExpenseButtonExpenseView):
                if row.index == index:
                    expense = str(expense).replace('.', ',')
                    row.text = "{:<11} {}".format(expense, category)


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

        self.button_new_expense = ButtonNewTask()
        self.button_new_expense.bind(on_press=self.switch_to_add_expense_page)
        self.add_widget(self.button_new_expense)

    @staticmethod
    def switch_to_todo_tasks_page(*args):
        back(direction='down', current='tasks')

    @staticmethod
    def switch_to_add_expense_page(*args):
        back(transition='no_transition', current='add_expense')

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
        self.expense = str(select[0][1])
        self.expense = self.expense.replace('.', ',')
        self.category = select[0][2]
        self.matter = select[0][3]
        self.date_add = select[0][4]

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
        self.button_cancel.bind(on_release=self.back)
        self.button_confirm.bind(on_release=self.insert_expense)

    def insert_expense(self, *args):
        if self.data_complete():
            if self.amount_money_correctly():
                expense_index = self.insert()
                gui = sm.get_screen('expenses').expenses
                gui.add_expense_to_gui(expense_index,
                                       self.expense_field.text,
                                       self.category_selector.text)
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
        self.button_cancel.bind(on_release=self.back)
        self.button_confirm.bind(on_release=self.confirm)
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

    def back(self, *args):
        back(direction='right', current='expenses')
        self.clear_the_fields()


class WindowManager(ScreenManager):
    pass


Builder.load_file("MyApp.kv")

sm = WindowManager()

screens = [Start(name='start'), ToDoTasksPage(name='tasks'), AddTaskPage(name='add_task'),
           MainWindow(name='task_window'), ExpensesPage(name='expenses'), AddExpensePage(name='add_expense'),
           ExpenseWindow(name='expense_window')]
for screen in screens:
    sm.add_widget(screen)

sm.current = 'start'
Start.done()


class MyApp(App):
    def build(self):
        # Window.clearcolor = (.376, .376, .376, 0)
        Window.clearcolor = (.85, .9, .85, .3)
        return sm


if __name__ == '__main__':
    MyApp().run()
    # do wyłączania aplikacji App.get_running_app().stop()
