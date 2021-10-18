from os import getenv
import re
from functools import partial
import time

from dotenv import load_dotenv
import kivy

# from kivy.interactive import InteractiveLauncher
from kivy.app import App
from kivy.lang import Builder
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
            if i != "":
                new_string.append(i)
        string = "\n".join(new_string)
        if len(string) > 300:
            return 'long'
        elif string != '':
            return string
        else:
            return False

    def tasks_from_db(self):
        select = self.database_connect.select_tasks('Tasks')
        tasks = []
        for index, task in select:
            tasks.append((index, task))

        return tasks

    def task_from_db(self, task_id):
        ...


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


class WrapButtonConfirm(WrapButton):
    def __init__(self, **kwargs):
        super(WrapButtonConfirm, self).__init__(**kwargs)

        self.text = 'Wykonane'
        self.background_normal = ''
        self.font_size = 16
        self.color = 'grey'
        self.size_hint = (0.08, None)
        self.size_hint_min_y = 20
        self.size_hint_min_x = 20


class WrapButtonNamed(WrapButton):
    def __init__(self, **kwargs):
        super(WrapButtonNamed, self).__init__(**kwargs)

        self.background_normal = ''
        self.font_size = 20
        self.color = 'grey'
        self.size_hint = (0.92, None)
        self.size_hint_min_y = 20
        self.size_hint_min_x = 20


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
        db = DatabaseValid()
        return db.tasks_from_db()

    @staticmethod
    def doorway(*instance):
        instance_id = instance[0].id
        MainWindow.current_id = instance_id
        sm.transition.direction = 'left'
        sm.current = 'task_window'

    def execute(self, *instance):
        instance_id = instance[0].id
        db = DatabaseValid()
        db.database_connect.mark_done('Tasks', instance_id)
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
        task = DatabaseValid.task_valid(task_from_kv)
        if task == 'long':
            popup = Popup(title='Ostrzeżenie',
                          content=Label(text="Tekst jest zbyt rozległy, skróć go."),
                          size_hint=(None, None), size=(400, 400)
                          )
            popup.open()
        elif task and task != 'long':
            db = DatabaseValid()
            db.database_connect.insert_task('Tasks', task)
            self.introduction_input.text = ''
            GridButtons.refresh_new_task()


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


class MainWindow(Screen):
    current_id = None
    task_content = ObjectProperty(None)
    task_date_of_performance = ObjectProperty(None)
    task = Task()

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
        self.task.receiving_content(self.current_id)

        self.task_content.text = self.task.task_content
        self.task_date_of_performance.text = self.task.task_date_of_performance

    def execute(self):
        db = DatabaseValid().database_connect
        db.mark_done(table='Tasks', index=self.current_id)

        GridButtons.refresh()
        self.button_back()

    def change_date_of_performance(self, *args):
        popup = Popup(title='Edycja',
                      content=Label(text=self.task_date_of_performance.text),
                      size_hint=(None, 200), size=(400, 400), auto_dismiss=False
                      )
        popup.open()

    def change_task_content(self, *args):
        changed_content = self.task_content.text
        task_validate = DatabaseValid.task_valid(changed_content)
        if task_validate:
            db = DatabaseValid()
            db.database_connect.update_task_content(table='Tasks', index=self.current_id, task=task_validate)
        GridButtons.refresh_new_task()


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
