from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label


class WrapButton(Button):
    def __init__(self, _id: int, **kwargs):
        super(WrapButton, self).__init__(**kwargs)
        self.id = _id

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, value):
        self.__id = value


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


class DayCalendarButton(Button):
    def __init__(self, _id: int, **kwargs):
        super(DayCalendarButton, self).__init__(**kwargs)
        self.id = _id

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, value):
        self.__id = value


class TitleCurrentDateWidget(BoxLayout):
    def __init__(self, **kwargs):
        super(TitleCurrentDateWidget, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint = (None, None)
        self.size = (160, 25)
        self.padding = 10
        self.height = 50
        # self.pos_hint = {'center_x': 0.2}


class SelectorMonthsWidget(BoxLayout):
    def __init__(self, **kwargs):
        super(SelectorMonthsWidget, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint = (0.32, 0.26)
        # self.size = (125, 300)
        # self.padding = 20
        # self.height = 80
        self.width = 200
        self.padding = 40
        self.spacing = 35
        # self.pos_hint = {'center_x': 0.7}


class CalendarLayoutWidget(GridLayout):
    def __init__(self, **kwargs):
        super(CalendarLayoutWidget, self).__init__(**kwargs)
        self.cols = 7
        self.rows = 7
        self.padding = 30
        self.spacing = 4
