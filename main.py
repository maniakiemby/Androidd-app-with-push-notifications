from os import getenv
import re
from functools import partial

from dotenv import load_dotenv
import kivy

# from kivy.interactive import InteractiveLauncher
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
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

from database import ConnectionDatabase

kivy.require('2.0.0')

load_dotenv()


class DatabaseValid:
    def __init__(self):
        self.database_connect = ConnectionDatabase(getenv('DB_NAME'))

    def __del__(self):
        self.database_connect.__del__()

    @staticmethod
    def task_valid(task):
        task = task.strip()
        new_string = []
        for i in task.splitlines():
            i = i.strip()
            i = re.sub("\s\s+", ' ', i)  # funkcja 'sub' zastępuje znalezione wyrażenia wybranym w drugim argumencie.
            if i is not "":
                new_string.append(i)
        string = "\n".join(new_string)
        if len(string) > 300:
            return 'long'
        elif string is not '':
            return string
        else:
            return False

    def tasks_from_db(self):
        select = self.database_connect.select_tasks('Tasks')
        tasks = []
        for index, task in select:
            tasks.append((index, task))

        return tasks

    def task_done(self, instance_id):
        self.database_connect.mark_done('Tasks', instance_id)


class WrapButton(Button):
    def __init__(self, _id, **kwargs):
        super(WrapButton, self).__init__(**kwargs)

        self.id = _id

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value


class MainTasksScrollVIew(ScrollView):
    def __init__(self, **kwargs):
        super(MainTasksScrollVIew, self).__init__(**kwargs)

        self.size = (Window.width, Window.height - 50)

    def grid_of_tasks(self):
        grid = GridButtons()
        self.add_widget(grid)

        return self


class GridButtons(GridLayout):
    def __init__(self, **kwargs):
        super(GridButtons, self).__init__(**kwargs)

        self.bind(minimum_height=self.setter('height'))

        self.all_tasks = self.receiving_tasks()

        for task in self.all_tasks:
            self.button_execute = WrapButton(text='Wykonane', on_release=self.execute, _id=task[0],
                                             background_normal='', font_size=16, color='grey', size_hint=(0.08, None),
                                             size_hint_min_y=20, size_hint_min_x=20
                                             )
            self.add_widget(self.button_execute)

            self.button = WrapButton(text=task[1], on_release=self.doorway, _id=task[0],
                                     background_normal='', font_size=20, color='black', size_hint=(0.92, None),
                                     size_hint_min_y=20, size_hint_min_x=20
                                     )
            self.add_widget(self.button)

    @staticmethod
    def receiving_tasks():
        db = DatabaseValid()
        return db.tasks_from_db()

    @staticmethod
    def doorway(*instance):
        instance_id = instance[0].id
        MainWindow.current_id = instance_id
        sm.switch_to(screens[1], direction='left')
        # sm.current = 'task_window'

    # @staticmethod
    def execute(self, *instance):
        instance_id = instance[0].id
        db = DatabaseValid()
        db.task_done(instance_id)
        for instance in self.walk():
            print(instance)
        # self.remove_widget(self.button)

        # TODO Dodać funkcjonalność, która będzie rozróżniała zadania i będzie je można usunąć za pomocą polecenia
        #  self.remove_widget(self.button)
        #  np. spróbuj nadać nazwę każdemu przyciskowi np 'button1', 'button2', itd.

    """def execute(self):
        db = DatabaseValid()
        db.task_done(instance_id)
        
    def remove_task(self, *instance):
        if self.button(_id=task_id) in self.walk():
            self.remove_widget(self.button(_id=task_id))
        else:
            print('Nie znalazłem widgetu')"""


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
        task = DatabaseValid.task_valid(task_from_kv)
        if task is 'long':
            popup = Popup(title='Ostrzeżenie',
                          content=Label(text="Tekst jest zbyt rozległy, skróć go."),
                          size_hint=(None, None), size=(400, 400)
                          )
            popup.open()
        elif task and task is not 'long':
            db = DatabaseValid()
            db.database_connect.insert_task('Tasks', task)
            self.introduction_input.text = ''


class Task:
    """This class is an aid to data tasks in the MainWindow class."""
    task_id = None
    task_content = ''
    task_date_add = None
    task_date_of_performance = None

    @classmethod
    def receiving_content(cls, task_id):
        db = DatabaseValid()
        task = db.database_connect.select_task('Tasks', task_id)
        cls.task_id = task[0][0]
        cls.task_content = task[0][1]
        cls.task_date_add = task[0][2]
        cls.task_date_of_performance = task[0][3]
        print(
            f'Task.receiving_content: {cls.task_id, cls.task_content, cls.task_date_add, cls.task_date_of_performance}'
        )


class MainWindow(Screen):
    current_id = None
    task_content = ObjectProperty(None)
    task_date_of_performance = ObjectProperty(None)

    @staticmethod
    def button_back():
        # sm.current = 'tasks'
        sm.switch_to(screens[0], direction='right')

    def on_enter(self, *args):
        task = Task()
        task.receiving_content(self.current_id)

        self.task_content.text = task.task_content
        self.task_date_of_performance.text = task.task_date_of_performance

    def execute(self):
        db = DatabaseValid()
        return db.task_done(self.current_id)


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
        # return ToDoTasks()
        return sm


if __name__ == '__main__':
    # launcher = InteractiveLauncher(MyApp())
    # launcher.run()
    MyApp().run()
