import os
import re
from datetime import datetime, date, time

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

from database import ConnectionDatabase, tasks_from_db, sort_tasks_by_date
from modules import DatePicker, TimePicker, ContentChanges
from my_uix import (WrapButtonConfirm,
                    WrapButtonNamed,
                    TaskBoardGridLayout,
                    ValidMessage,
                    ValidMessageYesOrNo,
                    ErrorMessage,
                    ValidMessageChangeYear,
                    IntroductionTextInput
                    )

kivy.require('2.0.0')
__version__ = "0.2"


class Start(Screen):
    def __init__(self, **kwargs):
        super(Start, self).__init__(**kwargs)
        os.system('ls > file_test.txt')

        with open('file_test.txt', 'r') as f:
            if 'database.db' in f.read():
                pass
            else:
                connection_database = ConnectionDatabase()
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
            self.button_execute = WrapButtonConfirm(on_release=self.execute, index=index)
            self.add_widget(self.button_execute)

            self.button_named = WrapButtonNamed(text=task[0], on_release=self.doorway, index=index, info='content')
            self.add_widget(self.button_named)

    @staticmethod
    def doorway(*instance):
        instance_id = instance[0].id
        MainWindow.current_id = instance_id
        sm.transition.direction = 'left'
        sm.current = 'task_window'

    def execute(self, *instance):
        instance_id = instance[0].id
        db = ConnectionDatabase()
        db.mark_done('Tasks', instance_id)
        self.refresh()

    @staticmethod
    def refresh():
        gui = sm.get_screen(name='tasks')
        for obj in gui.walk():
            if isinstance(obj, MainTasksScrollVIew):
                obj.clear_widgets()
                obj.add_widget(TaskBoard())


class MainTasksScrollVIew(ScrollView):
    def __init__(self, **kwargs):
        super(MainTasksScrollVIew, self).__init__(**kwargs)

        self.size = (Window.width, Window.height - 150)
        self.add_widget(TaskBoard())


class ToDoTasks(Screen):
    def __init__(self, **kwargs):
        super(ToDoTasks, self).__init__(**kwargs)
        self.new_task = None
        self.layout = GridLayout(cols=1, spacing=2)

        self.introduction_grid = GridLayout(cols=2)
        self.introduction_input = IntroductionTextInput()
        self.introduction_grid.add_widget(self.introduction_input)
        self.introduction_submit = Button(text="Dodaj", font_size=75, background_color='purple', size_hint=(0.4, 0.5),
                                          size_hint_min_x=50, size_hint_min_y=150)
        self.introduction_submit.bind(on_press=self.btn)
        self.introduction_grid.add_widget(self.introduction_submit)

        self.layout.add_widget(self.introduction_grid)

        grid = MainTasksScrollVIew()
        self.layout.add_widget(grid)
        self.add_widget(self.layout)

    def btn(self, instance):
        task_from_kv = self.introduction_input.text
        self.new_task = NewTask(task_from_kv)
        if self.new_task.task_content == 'long':
            popup = ValidMessage()
            popup.message_content.text = "Tekst jest zbyt rozległy, skróć go."
            popup.choice_layout.add_widget(Button(text='Ok', size=(0.2, 0.1), on_press=popup.dismiss))
            popup.open()
        elif self.new_task.task_content and self.new_task.task_content != 'long':
            if self.new_task.task_date_of_performance:
                datetime_now = '{} {}'.format(datetime.now().date().isoformat(),
                                              datetime.now().time().isoformat(timespec='seconds'))
                if self.new_task.task_date_of_performance < datetime_now:
                    popup = ValidMessageChangeYear()
                    popup.confirm.bind(on_press=self.change_year)
                    popup.cancel.bind(on_press=self.insert)

                    popup.open()
                else:
                    self.insert()
            else:
                self.insert()

    def change_year(self, *args):
        self.new_task.task_date_of_performance = date.fromisoformat(self.new_task.task_date_of_performance)
        self.new_task.task_date_of_performance = self.new_task.task_date_of_performance.replace(
            year=date.today().year + 1
        ).isoformat()
        self.insert()

    def insert(self, *args):
        db = ConnectionDatabase()
        db.insert_task(self.new_task.table_name, self.new_task.task_content, self.new_task.task_date_add,
                       self.new_task.task_date_of_performance, self.new_task.execution)
        self.introduction_input.text = ''
        TaskBoard.refresh()


class Task:
    def __init__(self, task_id):
        self.task_id = task_id
        self.task_content = None
        self.task_date_add = None
        self.task_date_of_performance = None

        self.task_date = None  # Must be datetime object
        self.task_time = None  # too

    def receiving_content(self):
        db = ConnectionDatabase()
        task = db.select_task('Tasks', self.task_id)
        self.task_content = task[0][1]
        self.task_date_add = task[0][2]
        self.task_date_of_performance = task[0][3]
        if self.task_date_of_performance != 'None':
            values = self.task_date_of_performance.split(sep=' ', maxsplit=1)
            self.task_date = date.fromisoformat(values[0])
            if len(values) == 2:
                self.task_time = time.fromisoformat(values[1])

    def update_data(self):
        if self.task_date:
            self.merge_date()
        db = ConnectionDatabase()
        try:
            db.update_task('Tasks',
                           self.task_id,
                           self.task_content,
                           self.task_date_of_performance)
        except ValueError:
            return False
        return True

    def merge_date(self):
        if self.task_time:
            self.task_date_of_performance = '{} {}'.format(
                self.task_date, self.task_time
            )

        else:
            self.task_date_of_performance = '{}'.format(
                self.task_date
            )


class NewTask:
    def __init__(self, input_task):
        self.table_name = 'Tasks'
        self._input_task = input_task
        self.task_date_add = '{} {}'.format(datetime.now().date().isoformat(),
                                            datetime.now().time().isoformat(timespec='seconds'))
        self.task_date_of_performance = None
        self.search_date_o_performance()
        self.task_content = self._input_task
        self.execution = 0

    def search_date_o_performance(self):
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

        regex_search_time = '(\s|^)\d{2}:\d{2}(\s|$)|(\s|^)\d:\d{2}(\s|$)'
        search_time = re.search(regex_search_time, self._input_task)
        if search_time:
            time_found = search_time.group(0).strip()
            if len(time_found) == 4:
                time_found = '0' + time_found
            self._input_task = re.sub(regex_search_time, '', self._input_task)

        regex_search_date = '(\s|^)\d{1,2}\s*\w{3}(\s|$)|(\s|^)\w{3}\s*\d{1,2}(\s|$)'
        search_date = re.search(regex_search_date, self._input_task)
        if search_date:
            date_found = search_date.group(0).strip().lower()
            self._input_task = re.sub(regex_search_date, '', self._input_task)

            month = re.sub('\d*\s*', '', date_found)
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
            if search_time:
                self.task_date_of_performance = '{date} {time}'.format(date=date_found, time=time_found)
            else:
                self.task_date_of_performance = date_found
        else:
            if search_time:
                self.task_date_of_performance = '{date} {time}'.format(
                    date=date.today().isoformat(), time=time_found
                )

    @property
    def task_content(self):
        return self.__task_content

    @task_content.setter
    def task_content(self, value):
        if len(value) == 0:
            self.__task_content = False
        elif len(value) > 300:
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
        result = self.task.update_data()
        self.back()
        if not result:
            ErrorMessage()

    @staticmethod
    def back(*args):
        sm.transition.direction = 'right'
        sm.current = 'tasks'
        TaskBoard.refresh()

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
        db = ConnectionDatabase()
        db.mark_done(table='Tasks', index=self.current_id)
        self.button_back()

    def change_date_of_performance(self, *args):

        if self.task.task_date is not None:
            date_picker = DatePicker(self.task.task_date)
        else:
            date_picker = DatePicker()

        app = App.get_running_app()
        app.popup = ModalView(size_hint=(None, None),
                              size=(430, 330),
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
        # TaskBoard.refresh()

    def change_time_of_performance(self, *args):
        if self.task.task_time is not None:
            time_picker = TimePicker(self.task.task_time)
        else:
            time_picker = TimePicker()
        app = App.get_running_app()
        app.popup = ModalView(size_hint=(None, None),
                              size=(300, 250),
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
        # TaskBoard.refresh()

    def change_task_content(self, *args):
        app = App.get_running_app()
        app.popup = ModalView(size_hint=(1, .5),
                              pos_hint={'x': .0, 'y': .3},
                              auto_dismiss=True,
                              on_dismiss=self.grab_content
                              )
        app.save_data = True
        content = ContentChanges(self.task.task_content)
        app.popup.add_widget(content)
        app.popup.open()

    def grab_content(self, *args):
        app = App.get_running_app()
        if app.save_data:
            _input_content = None
            for arg in args[0].walk(restrict=True):
                if isinstance(arg, TextInput):
                    _input_content = arg.text
                    break
            if _input_content == '':
                popup = ValidMessageYesOrNo()
                # popup.cancel.bind(on_press=popup.dismiss)
                popup.confirm.bind(on_press=self.execute)
                # popup.confirm.bind(on_press=popup.dismiss)
                popup.open()

            if 0 < len(_input_content) <= 300:
                for gui in self.walk():
                    if isinstance(gui, Label):
                        if gui.text == self.task.task_content:
                            gui.text = _input_content

                self.task.task_content = _input_content
                for gui in sm.get_screen('tasks').walk():
                    if isinstance(gui, WrapButtonNamed):
                        if gui.id == self.current_id and gui.info == 'content':
                            gui.text = self.task.task_content


class WindowManager(ScreenManager):
    pass


Builder.load_file("my.kv")

sm = WindowManager()

screens = [Start(name='start'), ToDoTasks(name='tasks'), MainWindow(name='task_window')]
for screen in screens:
    sm.add_widget(screen)

sm.current = 'start'
Start.done()


class MyApp(App):
    def build(self):
        Window.clearcolor = (.376, .376, .376, 0)
        return sm


if __name__ == '__main__':
    MyApp().run()
    # do wyłączania aplikacji App.get_running_app().stop()
