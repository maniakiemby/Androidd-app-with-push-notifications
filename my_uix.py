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
from kivy.uix.codeinput import CodeInput
from kivy.extras.highlight import KivyLexer
from kivy.uix.vkeyboard import VKeyboard


class Menu(BoxLayout):
    def __init__(self, current: str, **kwargs):
        super(Menu, self).__init__(**kwargs)
        self.menu_action_bar = MenuActionBar(current=current)
        self.menu_action_bar.background_color = (97/255, 97/255, 107/255, 1)
        self.add_widget(self.menu_action_bar)


class MenuActionPrevious(ActionPrevious):
    def __init__(self, **kwargs):
        super(MenuActionPrevious, self).__init__(**kwargs)

    @staticmethod
    def close_app(*args):
        ClosingAppMessage()


class MenuActionBar(ActionBar):
    def __init__(self, current: str, **kwargs):
        super(MenuActionBar, self).__init__(**kwargs)
        self.action_view = ActionView(use_separator=True)
        self.current = current  # tasks or notebook
        if self.current == 'tasks':
            self.action_previous = MenuActionPrevious(title='Moje zadania', with_previous=False)
            self.action_button = ActionButton(text='Zeszyt')
        else:
            self.action_previous = MenuActionPrevious(title='Zeszyt z wydatkami', with_previous=False)
            self.action_button = ActionButton(text='Moje zadania')

        self.action_view.add_widget(self.action_previous)
        self.action_view.add_widget(self.action_button)
        self.add_widget(self.action_view)


class ValidMessage(ModalView):
    def __init__(self, **kwargs):
        super(ValidMessage, self).__init__(**kwargs)
        self.layout = self.ids['layout']
        self.message_content = self.ids['message_content']
        self.choice_layout = self.ids['choice_layout']


class ConfirmationButtonWindowErrorMessage(Button):
    def __init__(self, **kwargs):
        super(ConfirmationButtonWindowErrorMessage, self).__init__(**kwargs)
        self.text = 'OK'


class ClosingAppMessage(ValidMessage):
    def __init__(self, **kwargs):
        super(ClosingAppMessage, self).__init__(**kwargs)
        self.message_content.text = 'Czy chcesz wyjść z aplikacji ?'
        self.choice_layout.cols = 2
        self.choice_layout.add_widget(
            ButtonWindowErrorMessageYes(on_press=self.yes))
        self.choice_layout.add_widget(
            ButtonWindowErrorMessageNo(on_press=self.dismiss))

        self.open()

    @staticmethod
    def yes(*args):
        Window.close()


class ButtonWindowErrorMessageYes(Button):
    def __init__(self, **kwargs):
        super(ButtonWindowErrorMessageYes, self).__init__(**kwargs)


class ButtonWindowErrorMessageNo(Button):
    def __init__(self, **kwargs):
        super(ButtonWindowErrorMessageNo, self).__init__(**kwargs)


class ErrorMessage(ValidMessage):
    def __init__(self, **kwargs):
        super(ErrorMessage, self).__init__(**kwargs)
        self.message_content.text = 'Wykonywana operacja nie powiodła się.'
        self.choice_layout.add_widget(
            ConfirmationButtonWindowErrorMessage(on_press=self.dismiss)
        )
        self.open()


class ValidMessageLongText(ValidMessage):
    def __init__(self, **kwargs):
        super(ValidMessageLongText, self).__init__(**kwargs)
        self.message_content.text = "Tekst jest zbyt rozległy, skróć go.\nMoże mieć maksymalnie 300 znaków."
        confirm_button = Button(text='Ok', on_press=self.dismiss)
        self.choice_layout.add_widget(confirm_button)


class ContentInput(CodeInput):
    def __init__(self):
        super(ContentInput, self).__init__()
        # self.lexer = KivyLexer()
        self.cursor_color = [0, 1, 0, 1]

    def insert_text(self, substring, from_undo=False):
        # regex_date = re.compile('(\s|^)\d{1,2}\s*\w{3}(\s|$)|(\s|^)\w{3}\s*\d{1,2}(\s|$)|$')
        # regex_time = re.compile('(\s|^)\d{2}:\d{2}(\s|$)|(\s|^)\d:\d{2}(\s|$)|$')
        #
        # search_date = regex_date.search(substring).group()
        # search_time = regex_time.search(substring).group()
        # text = substring
        # if search_date:
        #     text = text.replace(search_date, ' ')
        # if search_time:
        #     text = text.replace(search_time, ' ')

        if len(substring) > 350:
            substring = substring[:350]
            self.cursor_color = [1, 0, 0, 1]
        else:
            self.cursor_color = [0, 1, 0, 1]
        # else:
        #     s = ''.join([re.sub(self.pat, '', s) for s in substring])

        return super(ContentInput, self).insert_text(substring, from_undo=from_undo)


class TasksPageScrollView(ScrollView):
    def __init__(self, **kwargs):
        super(TasksPageScrollView, self).__init__(**kwargs)
        self.size = (Window.width, Window.height)


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


class ButtonBack(Button):
    def __init__(self, **kwargs):
        super(ButtonBack, self).__init__(**kwargs)


class ButtonNewItem(Button):
    def __init__(self, **kwargs):
        super(ButtonNewItem, self).__init__(**kwargs)


class ButtonConfirm(Button):
    def __init__(self, **kwargs):
        super(ButtonConfirm, self).__init__(**kwargs)


class RestoreInscription(WrapButton):
    def __init__(self, **kwargs):
        super(RestoreInscription, self).__init__(**kwargs)


class RestoreButton(WrapButton):
    def __int__(self, **kwargs):
        super(RestoreButton, self).__int__(**kwargs)


class RestoreDeletedEntry(FloatLayout):
    def __init__(self, index, **kwargs):
        super(RestoreDeletedEntry, self).__init__(**kwargs)
        self.restore_inscription = RestoreInscription(index=index, info='content')
        self.restore_button = RestoreButton(index=index, info='execute')

        # self.restore_inscription.add_widget(self.restore_button)

        self.add_widget(self.restore_inscription)
        # self.add_widget(self.restore_button)


#  below for application notebook


class CostNumberInput(TextInput):
    pat = re.compile('[0-9]*[,.]*[0-9]{2}')
    VKeyboard.layout = 'numeric'

    def insert_text(self, substring, from_undo=False):
        value = ''.join([re.sub(self.pat, '', value) for value in substring])

        return super(CostNumberInput, self).insert_text(value, from_undo=from_undo)


class ExpensesPageScrollView(ScrollView):
    def __init__(self, **kwargs):
        super(ExpensesPageScrollView, self).__init__(**kwargs)
        self.size = (Window.width, Window.height)


class ExpenseButtonExpenseView(WrapButton):
    pass
