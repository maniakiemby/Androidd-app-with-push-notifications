from os import getenv

from dotenv import load_dotenv
import kivy

# from kivy.interactive import InteractiveLauncher
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.properties import ObjectProperty

from database import ConnectionDb

kivy.require('2.0.0')

load_dotenv()


def tasks_from_db():
    db = ConnectionDb(getenv('DB_NAME'))
    select = db.select_tasks()
    tasks = [task[0] for task in select]
    print('ZADANIA:', tasks)

    return tasks


class ToDoApp(Screen):
    def __init__(self, **kwargs):
        super(ToDoApp, self).__init__(**kwargs)

        self.cols = 1

        self.inside = GridLayout()
        self.inside.cols = 2

        self.task = TextInput(multiline=False)
        self.add_widget(self.task)
        self.submit = Button(text="Dodaj", font_size=20)
        self.add_widget(self.submit)

        all_tasks = tasks_from_db()

        for task in all_tasks:
            self.inside.add_widget(Label(text=task))
            self.submit = (Button(text="Zobacz", font_size=10))
            self.submit.bind(on_press=self.vide)
            self.inside.add_widget(self.submit)

        self.add_widget(self.inside)

    def btn(self):
        print("zadanie:", self.new_task.text)
        task_from_kv = self.new_task.text
        if task_from_kv is not "":
            db = ConnectionDb(getenv('DB_NAME'))
            db.insert_task(table='Tasks', task=task_from_kv)
            self.new_task.text = ''

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


# kv = Builder.load_file("my.kv")

sm = WindowManager()

screens = [ToDoApp(name='tasks'), MainWindow(name='task_window')]
for screen in screens:
    sm.add_widget(screen)

sm.current = 'tasks'


class MyApp(App):
    def build(self):
        return ToDoApp()


if __name__ == '__main__':
    # launcher = InteractiveLauncher(MyApp())
    # launcher.run()
    MyApp().run()
