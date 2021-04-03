from os import getenv

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
from kivy.core.window import Window
from kivy.properties import ObjectProperty
from kivy.graphics import Color

from database import ConnectionDb

kivy.require('2.0.0')

load_dotenv()


def tasks_from_db():
    db = ConnectionDb(getenv('DB_NAME'))
    select = db.select_tasks()
    tasks = [task[0] for task in select]
    print('ZADANIA:', tasks)

    return tasks


class ToDo(GridLayout, Screen):
    def __init__(self, **kwargs):
        super(ToDo, self).__init__(**kwargs)

        self.cols = 1

        self.input_grid = GridLayout(cols=2, size_hint_y=None, height=100)
        self.input_new_task = TextInput(multiline=False)
        self.input_grid.add_widget(self.input_new_task)
        self.input_submit = Button(text="Dodaj", font_size=20)
        self.input_submit.bind(on_press=self.btn)
        self.input_grid.add_widget(self.input_submit)
        self.add_widget(self.input_grid)

        self.all_tasks = tasks_from_db()

        self.tasks_grid = GridLayout(cols=1, spacing=2, size_hint_y=None)
        self.tasks_grid.bind(minimum_height=self.tasks_grid.setter('height'))

        for task in self.all_tasks:
            button = Button(text=task, size_hint_y=None, font_size=18, background_color='purple', height=80)
            # submit.bind(on_press=self.vide)

            self.tasks_grid.add_widget(button)

        grid_of_tasks = ScrollView(size_hint=(1, None), size=(Window.width, Window.height - 100))
        grid_of_tasks.add_widget(self.tasks_grid)

        self.add_widget(grid_of_tasks)

    def btn(self, instance):
        # print("zadanie:", self.new_task.text)
        task_from_kv = self.input_new_task.text
        if task_from_kv is not "":
            print("zadanie:", self.input_new_task.text)
            db = ConnectionDb(getenv('DB_NAME'))
            db.insert_task(table='Tasks', task=task_from_kv)
            self.input_new_task.text = ''

            # self.add_widget(task_from_kv)
        else:
            print("nothink to add.")

    def vide(self, instance):
        sm.current = 'task_window'

        """
        db = ConnectionDb(getenv('DB_NAME'))
        db.delete_task(table='Tasks', task=task)
        """


class MainWindow(Screen):
    task = ObjectProperty(None)


class WindowManager(ScreenManager):
    pass


kv = Builder.load_file("MyApp.kv")

#sm = WindowManager()

#screens = [ToDoApp(name='tasks'), MainWindow(name='task_window')]
#for screen in screens:
 #   sm.add_widget(screen)

#sm.current = 'tasks'


class MyApp(App):
    def build(self):
        return ToDo()


if __name__ == '__main__':
    # launcher = InteractiveLauncher(MyApp())
    # launcher.run()
    MyApp().run()
