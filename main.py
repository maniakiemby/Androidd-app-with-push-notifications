from os import getenv
import re

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
from kivy.core.window import Window
from kivy.properties import ObjectProperty
from kivy.graphics import Color

from database import ConnectionDb

kivy.require('2.0.0')

load_dotenv()


def task_valid(task):
    task = task.strip()
    new_string = []
    for i in task.splitlines():
        i = i.strip()
        i = re.sub("\s\s+", ' ', i)  # funkcja 'sub' zastępuje znalezione wyrażenia wybranym w stringu.
        if i is not "":
            new_string.append(i)
    string = "\n".join(new_string)
    if len(string) < 300 and not '':
        return string
    else:
        return False


def tasks_from_db():
    db = ConnectionDb(getenv('DB_NAME'))
    select = db.select_tasks()
    tasks = [task[0] for task in select]
    print('ZADANIA:', tasks)

    return tasks


def delete_task(task):
    db = ConnectionDb(getenv('DB_NAME'))
    db.delete_task(table='Tasks', task=task)
    print("Wykonało się.")


class WrapButton(Button):
    pass


class MainTasksScrollVIew(ScrollView):
    def __init__(self, **kwargs):
        super(MainTasksScrollVIew, self).__init__(**kwargs)

        self.size_hint = (.5, None)
        self.size = (Window.width, Window.height - 50)

    def grid_of_tasks(self):
        grid = GridButtons()
        self.add_widget(grid)

        return self


class GridButtons(GridLayout):
    def __init__(self, **kwargs):
        super(GridButtons, self).__init__(**kwargs)

        self.cols = 1
        self.spacing = 2
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))

        self.all_tasks = tasks_from_db()

        for task in self.all_tasks:
            # deleting_button = Button(text="", font_size=25, background_normal='', color='grey',
            # size_hint_min_y=80, size_hint_max_x=80)

            # TODO: usuwa wszystko podczas inicjalizacji. Powinienem chyba powywalać więskszość z inita.
            #  deleting_button.bind(on_press=delete_task(task=task))
            # self.add_widget(deleting_button)
            button = WrapButton(text=task, background_normal='', font_size=20, color='black', size_hint=(1, None))
            button.bind(on_release=self.doorway)
            self.add_widget(button)

    @staticmethod
    def doorway(instance):
        sm.current = 'task_window'


class ToDoTasks(GridLayout, Screen):
    def __init__(self, **kwargs):
        super(ToDoTasks, self).__init__(**kwargs)

        self.cols = 1
        self.spacing = 2
        # self.size = (Window.width-10, Window.height)

        self.input_grid = GridLayout(cols=2)

        self.new_input = TextInput()
        self.input_grid.add_widget(self.new_input)

        self.input_submit = Button(text="Dodaj", font_size=20, background_color='purple', size_hint=(0.1, 0.1),
                                   size_hint_min_x=50, size_hint_min_y=50)
        self.input_submit.bind(on_press=self.btn)
        self.input_grid.add_widget(self.input_submit)

        self.add_widget(self.input_grid)

        grid = MainTasksScrollVIew().grid_of_tasks()
        self.add_widget(grid)

    def btn(self, instance):
        # print("zadanie:", self.new_task.text)
        task_from_kv = self.new_input.text
        task = task_valid(task_from_kv)
        print(task)
        if task:
            print("zadanie:", self.new_input.text)
            db = ConnectionDb(getenv('DB_NAME'))
            db.insert_task(table='Tasks', task=task)
            self.new_input.text = ''
            # ToDo self.tasks_grid.canvas.ask_updates()

            # ToDo self.add_widget(task_from_kv)
        else:
            print("nothink to add.")

    def __del__(self):
        return True


class MainWindow(Screen):
    task = ObjectProperty(None)


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
