from typing import Union
import re

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.modalview import ModalView


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


class ErrorMessage(ValidMessage):
    def __init__(self, **kwargs):
        super(ErrorMessage, self).__init__(**kwargs)

        self.size = (400, 125)
        self.message_content = 'Wykonywana operacja nie powiodła się.'
        self.choice_layout.add_widget(
            Button(text='Ok', size=(0.2, 0.1), on_press=self.dismiss)
        )
        self.open()


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


class IntroductionTextInput(TextInput):
    def __init__(self, **kwargs):
        super(IntroductionTextInput, self).__init__(**kwargs)
        self.focus = True

        self.hint_text = 'przykładowy format daty i godziny: 00:00 1sty | 1sty 1:08'


class TaskBoardGridLayout(GridLayout):
    def __init__(self, **kwargs):
        super(TaskBoardGridLayout, self).__init__(**kwargs)
        self.cols = 2
        self.background_normal = ''
        self.spacing = 2
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))


class WrapButton(Button):
    def __init__(self, index: int, info=Union[None, str], **kwargs):
        super(WrapButton, self).__init__(**kwargs)
        self.id = index
        self.info = info


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


class CalendarButtonDay(Button):
    def __init__(self, index: int, **kwargs):
        super(CalendarButtonDay, self).__init__(**kwargs)
        self.id = index


class TitleCurrentDateWidget(BoxLayout):
    def __init__(self, **kwargs):
        super(TitleCurrentDateWidget, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint = (None, None)
        self.size = (400, 25)
        self.padding = 10
        self.spacing = 30
        self.height = 50


class ButtonToday(Button):
    def __init__(self, **kwargs):
        super(ButtonToday, self).__init__(**kwargs)
        self.size_hint = (.25, 0.9)


class CancelButtonDate(Button):
    def __init__(self, **kwargs):
        super(CancelButtonDate, self).__init__(**kwargs)
        self.size_hint = (.25, 0.9)


class SelectorMonthsWidget(BoxLayout):
    def __init__(self, **kwargs):
        super(SelectorMonthsWidget, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint = (None, None)
        self.size = (400, 60)
        self.padding = 10
        self.spacing = 15


class SelectorMonthsLabel(Label):
    def __init__(self, **kwargs):
        super(SelectorMonthsLabel, self).__init__(**kwargs)
        self.font_size = 22
        self.pos = (0.5, 0.5)


class SelectorMonthsButtonPrevious(Button):
    def __init__(self, **kwargs):
        super(SelectorMonthsButtonPrevious, self).__init__(**kwargs)
        self.text = '<'
        self.width = 60
        self.size_hint = (0.12, 0.8)


class SelectorMonthsButtonNext(SelectorMonthsButtonPrevious):
    def __init__(self, **kwargs):
        super(SelectorMonthsButtonNext, self).__init__(**kwargs)
        self.text = '>'


class CalendarLayoutWidget(GridLayout):
    def __init__(self, **kwargs):
        super(CalendarLayoutWidget, self).__init__(**kwargs)
        self.cols = 7
        self.rows = 7
        self.padding = 30
        self.spacing = 4

        self.row_force_default = True
        self.row_default_height = 20
        # self.pos =
        # self.size = (1, 400)
        # self.minimum_size =


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
        self.size_hint = (None, None)
        self.font_size = 60
        self.center_x = 200


class CancelContentChangesButton(Button):
    def __init__(self, **kwargs):
        super(CancelContentChangesButton, self).__init__(**kwargs)
        self.size_hint = (.1, .1)
        self.text = 'Anuluj zmiany'
        # self.size = (.1, .3)
