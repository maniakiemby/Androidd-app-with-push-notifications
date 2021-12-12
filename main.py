from os import getenv
import re
# from functools import partial
from datetime import datetime, date, time
# from collections import namedtuple
from typing import Union

# from dotenv import load_dotenv
import kivy

# from kivy.interactive import InteractiveLauncher
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.modalview import ModalView
from kivy.uix.gridlayout import GridLayout
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

from database import ConnectionDatabase, tasks_from_db, task_from_db
# from tasks import CurrentTask, NewTask
from modules import DatePicker, TimePicker
from my_uix import WrapButton, WrapButtonConfirm, WrapButtonNamed

kivy.require('2.0.0')


# load_dotenv()


class GridButtons(GridLayout):
    def __init__(self, **kwargs):
        super(GridButtons, self).__init__(**kwargs)

        self.bind(minimum_height=self.setter('height'))

        self.all_tasks = self.receiving_tasks()

        for task in self.all_tasks:
            self.button_execute = WrapButtonConfirm(on_release=self.execute, _id=task[0])
            self.add_widget(self.button_execute)

            self.button_named = WrapButtonNamed(text=task[1], on_release=self.doorway, _id=task[0])
            self.add_widget(self.button_named)

    @staticmethod
    def receiving_tasks():
        # db = CurrentTask()
        return tasks_from_db()

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
        self.remove_task(instance_id)

    def remove_task(self, task_id):
        for widget in self.walk(restrict=True):
            try:
                if widget.id == task_id:
                    self.remove_widget(widget)
            except:
                pass

    @staticmethod
    def refresh(*args):
        if sm.has_screen(name='tasks'):
            sm.remove_widget(sm.get_screen('tasks'))
            sm.add_widget(ToDoTasks(name='tasks'))

        else:
            raise ScreenManagerException(
                "ScreenManager didn't found screen named 'tasks'"
            )

    @staticmethod
    def refresh_new_task(*args):
        if sm.has_screen(name='tasks'):
            sm.transition = NoTransition()
            sm.add_widget(ToDoTasks(name='new_tasks'))
            sm.current = 'new_tasks'
            sm.remove_widget(sm.get_screen('tasks'))
            sm.add_widget(ToDoTasks(name='tasks'))
            sm.current = 'tasks'
            sm.remove_widget(sm.get_screen('new_tasks'))
            sm.transition = SlideTransition()

        else:
            raise ScreenManagerException(
                "ScreenManager didn't found screen named 'tasks'"
            )


class MainTasksScrollVIew(ScrollView):
    def __init__(self, **kwargs):
        super(MainTasksScrollVIew, self).__init__(**kwargs)

        self.size = (Window.width, Window.height - 50)

    def grid_of_tasks(self):
        grid = GridButtons()
        self.add_widget(grid)

        return self


class ToDoTasks(Screen):
    def __init__(self, **kwargs):
        super(ToDoTasks, self).__init__(**kwargs)
        self.layout = GridLayout(cols=1, spacing=2)

        self.introduction_grid = GridLayout(cols=2)

        self.introduction_input = TextInput()
        self.introduction_grid.add_widget(self.introduction_input)

        self.introduction_submit = Button(text="Dodaj", font_size=20, background_color='purple', size_hint=(0.1, 0.1),
                                          size_hint_min_x=50, size_hint_min_y=50)
        self.introduction_submit.bind(on_press=self.btn)
        self.introduction_grid.add_widget(self.introduction_submit)

        self.layout.add_widget(self.introduction_grid)

        grid = MainTasksScrollVIew()
        grid.grid_of_tasks()
        self.layout.add_widget(grid)

        self.add_widget(self.layout)

    def btn(self, instance):
        task_from_kv = self.introduction_input.text
        new_task = NewTask(task_from_kv)
        if new_task.task_content == 'long':
            popup = Popup(title='Ostrzeżenie',
                          content=Label(text="Tekst jest zbyt rozległy, skróć go."),
                          size_hint=(None, None), size=(400, 400)
                          )
            popup.open()
        elif new_task.task_content and new_task.task_content != 'long':
            if new_task.task_date_of_performance:
                datetime_now = '{} {}'.format(datetime.now().date().isoformat(),
                                              datetime.now().time().isoformat(timespec='seconds'))
                if new_task.task_date_of_performance < datetime_now:
                    popup = Popup(title='Ostrzeżenie',
                                  content=Label(text="Czas wykonania zadania jest \nwcześniejszy, niż obecna data.\n"
                                                     "Czy chodziło Ci o wykonanie go w przyszłym roku ?"),
                                  size_hint=(None, None), size=(400, 400)
                                  )
                    popup.open()
            db = ConnectionDatabase()
            # insert_task(self, table, task, date_add=None, date_of_performance=None, execution=0)
            db.insert_task(new_task.table_name, new_task.task_content, new_task.task_date_add,
                           new_task.task_date_of_performance, new_task.execution)
            self.introduction_input.text = ''
            GridButtons.refresh_new_task()


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
        db = ConnectionDatabase()
        db.update_task('Tasks',
                       self.task_id,
                       self.task_content,
                       self.task_date_of_performance)


class NewTask:
    def __init__(self, input_task):
        self.table_name = 'Tasks'
        self.task_date_add = '{} {}'.format(datetime.now().date().isoformat(),
                                            datetime.now().time().isoformat(timespec='seconds'))
        self.task_date_of_performance = input_task
        self.task_content = input_task
        self.execution = 0
        print(self.task_date_of_performance)
        print(self.task_content)

    @property
    def task_date_of_performance(self):
        return self.__task_date_of_performance

    @task_date_of_performance.setter
    def task_date_of_performance(self, input_task):
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
        search_time = re.search(regex_search_time, input_task)
        if search_time:
            time_found = search_time.group(0).strip()
            if len(time_found) == 4:
                time_found = '0' + time_found
            input_task = re.sub(regex_search_time, '', input_task)
        _task_content = input_task

        regex_search_date = '(\s|^)\d{1,2}\s*\w{3}(\s|$)|(\s|^)\w{3}\s*\d{1,2}(\s|$)'
        search_date = re.search(regex_search_date, input_task)
        if search_date:
            date_found = search_date.group(0).strip().lower()
            _task_content = re.sub(regex_search_date, '', input_task)

            month = re.sub('\d*\s*', '', date_found)
            day = re.search('\d*', date_found).group(0)
            month_num = None
            for key, values in months.items():
                for word in values:
                    if month == word:
                        month_num = key
                        break
            date_found = date.fromisoformat(
                '{year}-{month}-{day}'.format(year=date.today().year, month=month_num, day=day))
            if date_found < date.today():
                date_found = date_found.replace(year=date.today().year + 1)
            date_found = date_found.isoformat()

            if search_time:
                self.__task_date_of_performance = '{date} {time}'.format(date=date_found, time=time_found)
            else:
                self.__task_date_of_performance = date_found
        else:
            if search_time:
                self.__task_date_of_performance = '{date} {time}'.format(
                    date=date.today().isoformat(), time=time_found
                )
            else:
                self.__task_date_of_performance = None
        self.task_content_change(_task_content)

    # TODO sprawić, aby self.task_content się zaktualizował

    def task_content_change(self, value):
        self.task_content = value


class MainWindow(Screen):
    current_id = None
    task_content = ObjectProperty(None)
    task_date_of_performance = ObjectProperty(None)
    task_time_of_performance = ObjectProperty(None)
    task = Task(current_id)

    def button_back(self):
        if self.task.task_content != self.task_content.text:
            # show = PopupSavingChangedContent()
            layout = FloatLayout()

            popup = Popup(title='Odrzucić zmiany ?',
                          content=layout,
                          size_hint=(None, None), size=(400, 180), auto_dismiss=False,
                          )

            label = Label(text='Wprowadzone zmiany nie zostaną zapisane.', size_hint=(.6, .2),
                          pos_hint={'x': .2, 'top': .88}
                          )
            button_cancel = Button(text='ANULUJ', size_hint=(.2, .1), pos_hint={'x': .1, 'y': .35})
            button_cancel.bind(on_press=popup.dismiss)
            button_discard = Button(text='ODRZUĆ', size_hint=(.2, .1), pos_hint={'x': .4, 'y': .35})
            button_discard.bind(on_press=self.back)
            button_discard.bind(on_press=popup.dismiss)
            button_save = Button(text='ZAPISZ', size_hint=(.2, .1), pos_hint={'x': .7, 'y': .35})
            button_save.bind(on_press=self.change_task_content)
            button_save.bind(on_press=self.back)
            button_save.bind(on_press=popup.dismiss)

            layout.add_widget(label)
            layout.add_widget(button_cancel)
            layout.add_widget(button_discard)
            layout.add_widget(button_save)

            popup.open()
        else:
            self.back()

    @staticmethod
    def back(*args):
        sm.transition.direction = 'right'
        sm.current = 'tasks'

    def on_enter(self, *args):
        self.task = Task(self.current_id)
        self.task.receiving_content()
        # print(task.task_id, task.task_content, task.task_date_of_performance)
        # self.task.task_id = self.current_id
        # self.task.receiving_content()

        self.task_content.text = self.task.task_content
        if self.task.task_date:
            self.task_date_of_performance.text = self.task.task_date.isoformat()
        else:
            self.task_date_of_performance.text = 'Dodaj datę'
        if self.task.task_time:
            self.task_time_of_performance.text = self.task.task_time.isoformat()
        else:
            self.task_time_of_performance.text = 'Dodaj czas'

    def execute(self):
        db = ConnectionDatabase()
        db.mark_done(table='Tasks', index=self.current_id)

        GridButtons.refresh()
        self.button_back()

    def change_date_of_performance(self, *args):
        if self.task.task_date is not None:
            date_picker = DatePicker(self.task.task_date)
        else:
            date_picker = DatePicker()
        popup = ModalView(size_hint=(.9, .6), pos_hint={'x': .05, 'y': .2}, auto_dismiss=True)
        popup.add_widget(date_picker)
        popup.open()
        new_date = date_picker.app.selected_date

    def change_time_of_performance(self, *args):
        if self.task.task_time is not None:
            time_picker = TimePicker(self.task.task_time)
        else:
            time_picker = TimePicker()
        popup = ModalView(size_hint=(.9, .6), pos_hint={'x': .05, 'y': .2}, auto_dismiss=True)
        popup.add_widget(time_picker)
        popup.open()

    def change_task_content(self, *args):
        popup = ModalView(size_hint=(1, .6), pos_hint={'x': .0, 'y': .0}, auto_dismiss=True)
        text_input = TextInput(text=self.task.task_content)
        popup.add_widget(text_input)
        # popup.bind(on_dismiss=self.save_content)
        popup.open()

        self.task.task_content = text_input.text
        self.task_content.text = text_input.text

        # TODO Wymyśleć coś, aby podczas wyłączania okienka zapisywały się zmiany

        print(self.task.task_content)


class WindowManager(ScreenManager):
    pass


kv = Builder.load_file("MyApp.kv")

sm = WindowManager()

screens = [ToDoTasks(name='tasks'), MainWindow(name='task_window')]
for screen in screens:
    sm.add_widget(screen)

sm.current = 'tasks'


class MyApp(App):
    def build(self):
        Window.clearcolor = (.376, .376, .376, 0)
        return sm


if __name__ == '__main__':
    # launcher = InteractiveLauncher(MyApp())
    # launcher.run()
    MyApp().run()
    # do wyłączania aplikacji App.get_running_app().stop()
