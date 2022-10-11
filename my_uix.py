from typing import Union
import re
from datetime import datetime

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.modalview import ModalView
from kivy.uix.image import Image
from kivy.graphics import BorderImage
from kivy.uix.actionbar import ActionBar, ActionView, ActionGroup, ActionButton, ActionPrevious
from kivy.uix.dropdown import DropDown


class Menu(BoxLayout):
    def __init__(self, current: str, **kwargs):
        super(Menu, self).__init__(**kwargs)
        self.menu_action_bar = MenuActionBar(current=current)
        self.add_widget(self.menu_action_bar)


class MenuActionBar(ActionBar):
    def __init__(self, current: str, **kwargs):
        super(MenuActionBar, self).__init__(**kwargs)
        self.action_view = ActionView(use_separator=True)
        self.current = current  # tasks or notebook
        if self.current == 'tasks':
            self.action_previous = ActionPrevious(title='Moje zadania', with_previous=False)
            self.action_button = ActionButton(text='Zeszyt')
        else:
            self.action_previous = ActionPrevious(title='Zeszyt z wydatkami', with_previous=False)
            self.action_button = ActionButton(text='Moje zadania')

        self.action_view.add_widget(self.action_previous)
        self.action_view.add_widget(self.action_button)
        self.add_widget(self.action_view)

        # self.text = 'Wybór'
        # self.mode = 'spinner'
        # self.action_button_tasks = ActionButton(text='zadania')
        # self.action_button_notebook = ActionButton(text='zeszyt')
        #
        # self.add_widget(self.action_button_tasks)
        # self.add_widget(self.action_button_notebook)


class ValidMessage(ModalView):
    def __init__(self, **kwargs):
        super(ValidMessage, self).__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (400, 210)
        self.auto_dismiss = True

        self.layout = BoxLayout(orientation='vertical')
        self.message_content = Label()
        self.layout.add_widget(self.message_content)

        self.choice_layout = GridLayout(
            cols=1, padding=22, spacing=5
        )
        self.layout.add_widget(self.choice_layout)

        self.add_widget(self.layout)


class IntroductionModalView(ModalView):
    def __init__(self, **kwargs):
        super(IntroductionModalView, self).__init__(**kwargs)
        self.auto_dismiss = False
        self.background_color = (0, 0, 0, .2)
        self.pos_hint = {'x': 0, 'y': .3}
        self.size_hint = (1, .7)


class ErrorMessage(ValidMessage):
    def __init__(self, **kwargs):
        super(ErrorMessage, self).__init__(**kwargs)
        self.size = (400, 225)
        self.message_content.text = 'Wykonywana operacja nie powiodła się.'
        self.choice_layout.add_widget(
            Button(text='Ok', size=(0.2, 1), on_press=self.dismiss)
        )
        self.open()


class ValidMessageLongText(ValidMessage):
    def __init__(self, **kwargs):
        super(ValidMessageLongText, self).__init__(**kwargs)
        self.message_content.text = "Tekst jest zbyt rozległy, skróć go.\nMoże mieć maksymalnie 300 znaków."
        confirm_button = Button(text='Ok', on_press=self.dismiss)
        self.choice_layout.add_widget(confirm_button)


class ValidMessageYesOrNo(ValidMessage):
    def __init__(self, **kwargs):
        super(ValidMessageYesOrNo, self).__init__(**kwargs)
        self.auto_dismiss = False
        self.message_content.text = 'Brak opisu zadania. Czy chcesz usunąć to zadanie ?'

        self.choice_layout.cols = 2
        self.confirm = Button(text='Tak', size=(0.2, 0.1))
        self.confirm.bind(on_press=self.dismiss)
        self.choice_layout.add_widget(self.confirm)
        self.cancel = Button(text='Nie', size=(0.2, 0.1))
        self.cancel.bind(on_press=self.dismiss)
        self.choice_layout.add_widget(self.cancel)


class ValidMessageChangeYear(ValidMessageYesOrNo):
    def __init__(self, **kwargs):
        super(ValidMessageChangeYear, self).__init__(**kwargs)
        self.message_content.text = "Czas wykonania zadania jest \nwcześniejszy, niż obecna data.\n" \
                                    "Czy chodziło Ci o wykonanie go w przyszłym roku ?"
        self.app = App.get_running_app()
        self.cancel.bind(on_press=self.on_cancel)
        self.confirm.bind(on_press=self.on_confirm)

    def on_confirm(self, *args):
        app = App.get_running_app()
        app.save_data = True
        self.dismiss()

    def on_cancel(self, *args):
        app = App.get_running_app()
        app.save_date = False
        self.dismiss()


# TODO stworzyć klasę bazową i dwie klasy dziedziczące, oddzielnie do dodawania nowego zadania
#  i do edycji zadania
#  klasa dodająca nowe zadanie ma zajmować się separacją daty i czasu we właściwy sposób.
#  Do tego właściwie podkreślać za długi tekst (obecnie tekst jest skracany o datę i czas,
#  a podkreślenie wynikające ze zbyt długiego tekstu nie bierze tego pod uwagę).

class IntroductionNewContent(TextInput):
    def __init__(self, **kwargs):
        super(IntroductionNewContent, self).__init__(**kwargs)
        self.input_type = 'text'
        self.multiline = False
        self.font_size = 65

        self.pos_hint = {'x': .05, 'y': .55}
        self.size_hint = (0.9, 0.2)
        self.hint_text = '00:00 1sty | 1sty 1:08'

    # def on_text(self, instance, value):
    #     if len(value) >= 300:
    #         self.background_color = [1, .141, .2, 1]
    #     super(IntroductionNewContent, self).on_text(instance, value)

    """def insert_text(self, substring, from_undo=True):
        if len(self.text) >= 300:
            self.background_color = [1, .141, .2, 1]
        super(IntroductionNewContent, self).insert_text(substring, from_undo)

    def do_backspace(self, from_undo=True, mode='bkspc'):
        if len(self.text) <= 301:
            self.background_color = [1, 1, 1, .8]
        super(IntroductionNewContent, self).do_backspace(from_undo, mode)
    """


class TasksPageScrollView(ScrollView):
    def __init__(self, **kwargs):
        super(TasksPageScrollView, self).__init__(**kwargs)
        self.size = (Window.width, Window.height)
        self.button_new_task_obj = None
        self.direction_value = None

    def on_touch_down(self, touch):
        if self.direction_value is not None:
            if touch.pos[1] > self.direction_value:
                self.button_new_task_obj.show()
            elif touch.pos[1] < self.direction_value:
                self.button_new_task_obj.hide()
        self.direction_value = touch.pos[1]

        super(TasksPageScrollView, self).on_touch_down(touch)


class WrapButton(Button):
    def __init__(self, index: int, info: Union[None, str], **kwargs):
        super(WrapButton, self).__init__(**kwargs)
        self.index = index
        self.info = info


class ExecuteButtonTasksView(WrapButton):
    def __init__(self, **kwargs):
        super(ExecuteButtonTasksView, self).__init__(**kwargs)


class TaskButtonTasksView(WrapButton):
    def __init__(self, **kwargs):
        super(TaskButtonTasksView, self).__init__(**kwargs)


class CalendarButtonDay(Button):
    def __init__(self, index: int, **kwargs):
        super(CalendarButtonDay, self).__init__(**kwargs)
        self.id = index
        # self.size_hint = (.15, .15)
        # self.size = (100,100)


class TitleCurrentDateWidget(BoxLayout):
    def __init__(self, **kwargs):
        super(TitleCurrentDateWidget, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint = (1, .25)
        self.size = (400, 25)
        # self.padding = 10
        self.spacing = 30
        # self.height = 50


class ButtonToday(Button):
    def __init__(self, **kwargs):
        super(ButtonToday, self).__init__(**kwargs)
        self.size_hint = (.4, .5)
        self.pos_hint = {'top': .75}
        self.text = 'Dziś'


class CancelButtonDate(Button):
    def __init__(self, **kwargs):
        super(CancelButtonDate, self).__init__(**kwargs)
        self.size_hint = (.4, .5)
        self.pos_hint = {'top': .75}
        self.text = 'Anuluj'
        # self.


class SelectorMonthsWidget(BoxLayout):
    def __init__(self, **kwargs):
        super(SelectorMonthsWidget, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint = (1, .25)
        # self.size = (400, 200)
        self.padding = 10
        self.spacing = 30


class SelectorMonthsLabel(Label):
    def __init__(self, **kwargs):
        super(SelectorMonthsLabel, self).__init__(**kwargs)
        self.font_size = 100
        self.pos = (1, 1)


class SelectorMonthsButtonPrevious(Button):
    def __init__(self, **kwargs):
        super(SelectorMonthsButtonPrevious, self).__init__(**kwargs)
        self.text = '<'
        self.size_hint = (.2, .5)
        self.pos_hint = {'top': .75}


class SelectorMonthsButtonNext(SelectorMonthsButtonPrevious):
    def __init__(self, **kwargs):
        super(SelectorMonthsButtonNext, self).__init__(**kwargs)
        self.text = '>'


class CalendarLayoutWidget(GridLayout):
    def __init__(self, **kwargs):
        super(CalendarLayoutWidget, self).__init__(**kwargs)
        # self.row_force_default = True
        # self.row_default_height = 100


class EnteringTimeBox(BoxLayout):
    def __init__(self, **kwargs):
        super(EnteringTimeBox, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        # self.size_hint = (None, None)
        self.size = (350, 500)


class CancelButtonTime(Button):
    def __init__(self, **kwargs):
        super(CancelButtonTime, self).__init__(**kwargs)
        self.text = 'Anuluj'
        self.size_hint = (0.1, 0.3)


class NumberInput(TextInput):
    pat = re.compile('[^0-9]')

    def insert_text(self, substring, from_undo=False):
        if len(self.text) > 1:
            s = ''
        else:
            s = ''.join([re.sub(self.pat, '', s) for s in substring])

        return super(NumberInput, self).insert_text(s, from_undo=from_undo)


class TimeInput(NumberInput):
    def __init__(self, **kwargs):
        super(TimeInput, self).__init__(**kwargs)
        self.input_type = 'number'
        self.size_hint = (1, 1)
        self.font_size = 60
        self.center_x = 200


class CancelContentChangesButton(Button):
    def __init__(self, **kwargs):
        super(CancelContentChangesButton, self).__init__(**kwargs)
        self.pos_hint = {'x': 0, 'top': 1}
        self.size_hint = (.13, .12)
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ''


class ButtonNewTask(Button):
    def __init__(self, **kwargs):
        super(ButtonNewTask, self).__init__(**kwargs)
        self.pos_hint = {'x': .65, 'top': .2}
        self.size_hint = (.15, .08)
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ''

    def hide(self):
        self.pos_hint = {'x': .65, 'top': .9}

    def show(self):
        self.pos_hint = {'x': .65, 'top': .2}


class ConfirmAddingButton(Button):
    def __init__(self, **kwargs):
        super(ConfirmAddingButton, self).__init__(**kwargs)
        self.pos_hint = {'x': .6, 'top': .3}
        self.size_hint = (.3, .15)
        self.background_color = (0, 0, 0, .5)
        self.background_normal = ''
        self.font_size = 65
        self.text = 'dodaj'


#  below for application notebook


class CostNumberInput(TextInput):
    pat = re.compile('[0-9]*[,.]*[0-9]{2}')

    def insert_text(self, substring, from_undo=False):
        value = ''.join([re.sub(self.pat, '', value) for value in substring])

        return super(CostNumberInput, self).insert_text(value, from_undo=from_undo)


class ExpensesPageScrollView(ScrollView):
    def __init__(self, **kwargs):
        super(ExpensesPageScrollView, self).__init__(**kwargs)
        self.size = (Window.width, Window.height)


class CategorySelector:
    def __init__(self, **kwargs):
        super(CategorySelector, self).__init__(**kwargs)
        # https://kivy.org/doc/stable/api-kivy.uix.dropdown.html
        self.dropdown = DropDown()


class ExpenseButtonExpenseView(WrapButton):
    pass
    # def __init__(self, **kwargs):
    #     super(ExpenseButtonExpenseView, self).__init__(**kwargs)
