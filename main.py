import os
import re
from datetime import datetime, date, time
import pdb

import kivy
# from kivy.interactive import InteractiveLauncher
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.modalview import ModalView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen, ScreenManagerException, \
    FadeTransition, SlideTransition, NoTransition
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.recycleview import views
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.properties import ObjectProperty
from kivy.graphics import Color

from database import ConnectionDatabaseTasks, tasks_from_db, sort_tasks_by_date, ConnectionDatabaseExpenses, \
    ConnectionDatabaseCategoriesExpenses, ConnectionDatabaseExpenseData
from modules import DatePicker, TimePicker, Content, list_of_categories
from my_uix import (Menu,
                    TasksPageScrollView, TaskBoardGridLayout, WrapButton, ExecuteButtonTasksView,
                    TaskButtonTasksView,  # TaskGridLayoutTaskBoard,
                    ValidMessage, ErrorMessage, ValidMessageLongText, ValidMessageYesOrNo, ValidMessageChangeYear,
                    ButtonNewTask, IntroductionModalView,
                    CategorySelector, ExpensesPageScrollView, ButtonExpense,
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
                connection_database = ConnectionDatabaseCategoriesExpenses()
                connection_database.create_table()
                connection_database = ConnectionDatabaseExpenseData()
                connection_database.create_table()
        os.system('rm file_test.txt')

    @staticmethod
    def done():
        sm.transition.direction = 'down'
        sm.current = 'tasks'


class TaskBoard(TaskBoardGridLayout):
    def __init__(self, **kwargs):
        super(TaskBoard, self).__init__(**kwargs)
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
        sm.transition.direction = 'left'
        sm.current = 'task_window'

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
        self.button_adding_new_task.bind(on_press=self.add_task_screen)

        self.scroll_view = TasksPageScrollView()
        self.scroll_view.button_new_task_obj = self.button_adding_new_task
        self.task_board = TaskBoard()
        self.scroll_view.add_widget(self.task_board)

        self.add_widget(self.menu)
        self.add_widget(self.scroll_view)
        self.add_widget(self.button_adding_new_task)

    @staticmethod
    def add_task_screen(*args):
        sm.transition = NoTransition()
        sm.current = 'add_task'
        sm.transition = SlideTransition()

    @staticmethod
    def switch_to_expenses_page(*args):
        sm.transition.direction = 'right'
        sm.current = 'expenses'


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


class NewTaskPage(Screen):
    def __init__(self, **kwargs):
        super(NewTaskPage, self).__init__(**kwargs)
        self.content = Content(behavior='new data')
        self.content.text_input.is_focusable = True
        self.content.text_input.bind(on_text_validate=self.grab_content_of_new_task)  # event 'on_enter'
        self.content.confirm_adding.bind(on_press=self.grab_content_of_new_task)
        self.content.cancel_button.bind(on_press=self.back)
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
                elif self.new_task.task_date_of_performance:
                    if self.new_task.task_date_of_performance < self.new_task.task_date_add:
                        popup = ValidMessageChangeYear()
                        popup.confirm.bind(on_press=self.change_year)
                        popup.cancel.bind(on_press=self.insert)
                        popup.open()
                else:
                    self.insert()

    def change_year(self, *args):
        self.new_task.task_date_of_performance = date.fromisoformat(self.new_task.task_date_of_performance)
        self.new_task.task_date_of_performance = self.new_task.task_date_of_performance.replace(
            year=date.today().year + 1
        ).isoformat()
        self.insert()

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
    def back(*args):
        sm.transition = NoTransition()
        sm.current = 'tasks'
        sm.transition = SlideTransition()


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
            date_found = search_date.group(0).strip().lower()
            self.input_task = re.sub(regex_search_date, '', self.input_task)

            month = re.sub('\d*\s*', '', date_found)
            months_names = []
            [months_names.extend(name) for name in months.values()]
            if month in months_names:
                day = re.search('\d*', date_found).group(0)
                if len(day) == 1:
                    day = '0' + day
                month_num = None
                for key, values in months.items():
                    for word in values:
                        if month == word:
                            month_num = key
                            break
                date_found = '{year}-{month}-{day}'.format(year=date.today().year, month=month_num, day=day)
                try:
                    date.fromisoformat(date_found)
                except ValueError:
                    'day is out of range for month'
                    date_found = None
            else:
                search_date = None

        regex_search_time = '(\s|^)\d{2}:\d{2}(\s|$)|(\s|^)\d:\d{2}(\s|$)'
        search_time = re.search(regex_search_time, self.input_task)
        if search_time:
            time_found = search_time.group(0).strip()
            if len(time_found) == 4:
                time_found = '0' + time_found
            self.input_task = re.sub(regex_search_time, '', self.input_task)

        if search_date:
            if search_time:
                self.task_date_of_performance = '{date} {time}'.format(date=date_found, time=time_found)
            else:
                self.task_date_of_performance = date_found
        else:
            if search_time:
                self.task_date_of_performance = '{date} {time}'.format(
                    date=date.today().isoformat(), time=time_found
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
        self.back()
        if not result:
            ErrorMessage()

    @staticmethod
    def back(*args):
        sm.transition.direction = 'right'
        sm.current = 'tasks'

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
        self.back()

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
                    popup = ValidMessage()
                    popup.message_content.text = "Wprowadź poprawną godzinę\nw formacie 24h:60m"
                    popup.choice_layout.add_widget(Button(text='Ok', size=(0.2, 0.1), on_press=popup.dismiss))
                    popup.open()

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
        self.cols = 1
        self.spacing = 3
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))

        db = ConnectionDatabaseExpenses()
        self.all_expenses = db.select_expenses()

        for expense in self.all_expenses.values():
            self.add_expense_to_gui(expense[0], expense[1])

    def add_expense_to_gui(self, expense, category):
        label = ButtonExpense(text="{} {}".format(expense, category))
        self.add_widget(label)


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
        sm.transition.direction = 'left'
        sm.current = 'tasks'

    @staticmethod
    def switch_to_add_expense_page(*args):
        sm.transition = NoTransition()
        sm.current = 'add_expense'
        sm.transition = SlideTransition()

    # TODO link do XAMPP czyli narzędzia budującego lokalny host na komputerze.
    #  https://stackoverflow.com/questions/42704846/running-python-scripts-with-xampp
    #  https://blog.terresquall.com/2021/10/running-python-in-xampp/


class Expense:
    def __init__(self):
        self.expense = None
        self.category = None
        self.matter = None
        self.date_add = None


class NewExpensePage(Screen):
    def __init__(self, **kwargs):
        super(NewExpensePage, self).__init__(**kwargs)
        self.date_add = datetime.now().date().isoformat()
        self.expense_field = self.ids['expense']
        self.matter_field = self.ids['matter']
        self.button_date_add = self.ids['date_add']
        self.button_date_add.text = self.date_add
        self.date_picker = None
        self.button_cancel = self.ids['cancel']
        self.button_confirm = self.ids['confirm']

        self.categories = list_of_categories()
        self.category_selector = self.ids['category']
        self.dropdown = DropDown()
        for category in self.categories:
            self.button_category = Button(text=category, size_hint_y=None, height=30)
            self.button_category.bind(on_release=lambda button_category: self.dropdown.select(button_category.text))
            self.dropdown.add_widget(self.button_category)
        self.category_selector.bind(on_release=self.dropdown.open)
        self.category_selector.auto_width = False
        self.dropdown.bind(on_select=lambda instance, x: setattr(self.category_selector, 'text', x))

    def open_date_picker(self):
        the_set_date = self.button_date_add.text
        if the_set_date:
            self.date_picker = DatePicker(date.fromisoformat(the_set_date))
        else:
            self.date_picker = DatePicker()
        app = App.get_running_app()
        app.popup = ModalView(size_hint=(None, None),
                              size=(Window.width - 25, Window.height / 1.7),
                              auto_dismiss=True,
                              on_dismiss=self.grab_date
                              )
        app.popup.add_widget(self.date_picker)
        app.save_data = True
        app.popup.open()

    def grab_date(self, *args):
        app = App.get_running_app()
        if app.save_data:
            self.date_add = self.date_picker.selected_date.isoformat()
            self.button_date_add.text = self.date_add

    def data_complete(self):
        if self.category_selector.text == 'wybierz kategorię' or self.expense_field.text == '':
            popup = ValidMessage()
            popup.message_content.text = "Wpis nie jest zupełny."
            popup.choice_layout.add_widget(Button(text='Ok', size=(0.2, 0.1), on_press=popup.dismiss))
            popup.open()
            return False
        return True

    def clear_the_fields(self):
        self.expense_field.text = ''
        self.dropdown.select('wybierz kategorię')  # this string must too same in .kv file under id: category
        self.matter_field.text = ''
        self.button_date_add.text = self.date_add

    @staticmethod
    def back(*args):
        sm.transition = NoTransition()
        sm.current = 'expenses'
        sm.transition = SlideTransition()

    def insert_expense(self, *args):
        # this button will add new expense report and will clear all fields
        if self.data_complete():
            self.insert()

    def insert(self):
        db = ConnectionDatabaseExpenses()
        res = db.insert_expense(expense=self.expense_field.text,
                                matter=self.matter_field.text,
                                category_id=self.category_selector.text,
                                date_add=self.date_add)
        print(res, self.category_selector.text)
        self.clear_the_fields()


class WindowManager(ScreenManager):
    pass


Builder.load_file("MyApp.kv")

sm = WindowManager()

screens = [Start(name='start'), ToDoTasksPage(name='tasks'), NewTaskPage(name='add_task'),
           MainWindow(name='task_window'), ExpensesPage(name='expenses'), NewExpensePage(name='add_expense')]
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
