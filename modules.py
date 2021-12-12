from datetime import date, time, datetime, timedelta
import calendar

# from kivy.uix.modalview import ModalView
# from kivy.uix.textinput import TextInput
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty

from my_uix import (DayCalendarButton,
                    TitleCurrentDateWidget,
                    SelectorMonthsWidget,
                    CalendarLayoutWidget
                    )


Builder.load_file('pickers.kv')
# TODO link do strony z takim kalendarzem
#  https://stackoverflow.com/questions/13714074/kivy-date-picker-widget


class DatePicker(GridLayout):  # data musi być w formacie '2021-11-26' i obiektem datetime
    def __init__(self, date_value=date.today(), **kwargs):
        super(DatePicker, self).__init__(**kwargs)
        self.rows = 5

        self.app = App.get_running_app()
        self.app.selected_date = date_value

        self.title_current_date = TitleCurrentDate(self.app.selected_date)
        # self.title_current_date.current_date = self.selected_date
        self.add_widget(self.title_current_date)

        self.selector_months = SelectorMonths(self.app.selected_date.year, self.app.selected_date.month)
        self.add_widget(self.selector_months)

        self.calendar_layout = CalendarLayout(self.app.selected_date.month,
                                              self.app.selected_date.year,
                                              self.app.selected_date.day
                                              )
        self.add_widget(self.calendar_layout)

    # TODO A MOŻE SPRÓBOWAĆ STWORZYĆ WZAJEMNE POWIĄZANIA,
    #  TAK ŻEBY TE KLASY DZIEDZICZYŁY PO SOBIE ŁAŃCUCHEM
    def refresh(self):
        self.clear_widgets()
        self.__init__(self.app.selected_date)


class TitleCurrentDate(TitleCurrentDateWidget):
    def __init__(self, current_date, **kwargs):
        super(TitleCurrentDate, self).__init__(**kwargs)
        self.current_date = '{}/{}/{}'.format(current_date.day, current_date.month, current_date.year)  # 26/11/2021
        self.date_label = Label(text=self.current_date, font_size=22)
        self.add_widget(self.date_label)


class SelectorMonths(SelectorMonthsWidget):
    def __init__(self, year: int, month: int, **kwargs):
        super(SelectorMonths, self).__init__(**kwargs)
        self.app = App.get_running_app()
        self.month = month
        self.year = year
        self.month_names = ['Styczeń',
                            'Luty',
                            'Marzec',
                            'Kwiecień',
                            'Maj',
                            'Czerwiec',
                            'Lipiec',
                            'Sierpień',
                            'Wrzesień',
                            'Październik',
                            'Listopad',
                            'Grudzień'
                            ]
        self._format = '{} {}'.format(self.month_names[self.month - 1], self.year)

        self.app.print_date = Label(text=self._format, font_size=25)
        self.add_widget(self.app.print_date)
        self.previous_month = Button(text='<')
        self.previous_month.bind(on_press=self.go_previous_month)
        self.add_widget(self.previous_month)
        self.next_month = Button(text='>')
        self.next_month.bind(on_press=self.go_next_month)
        self.add_widget(self.next_month)

    def go_next_month(self, *args):
        if self.month == 12:
            self.year += 1
            self.month = 1
        else:
            self.month += 1
        self.change_month()

    def go_previous_month(self, *args):
        if self.month == 1:
            self.year -= 1
            self.month = 12
        else:
            self.month -= 1
        self.change_month()

    def change_month(self):
        self.app.print_date.text = '{} {}'.format(
            self.month_names[self.month - 1], self.year)
        self.app.selected_date = self.app.selected_date.replace(month=self.month, year=self.year)

        # TODO ZNALEŹĆ SPOSÓB NA ODŚWIERZENIE WIDOKU
        DatePicker.refresh


class CalendarLayout(CalendarLayoutWidget):
    def __init__(self, month: int, year: int, day=None, **kwargs):
        super(CalendarLayout, self).__init__(**kwargs)
        self.app = App.get_running_app()
        self.day = day
        self.month = month
        self.year = year
        days = ['Pon', 'Wt', 'Śr', 'Czw', 'Pt', 'So', 'Nd']
        for day in days:
            name_of_the_day = Label(text=day)
            self.add_widget(name_of_the_day)

        monthrange = calendar.monthrange(self.year, self.month)
        self.first_day_month = monthrange[0]
        self.days_in_month = monthrange[1]

        _id = 0
        for number in range(self.days_in_month):
            while self.first_day_month > _id:
                day = Label(text='')
                self.add_widget(day)
                _id += 1
            day = DayCalendarButton(text=str(number + 1), _id=(number + 1))
            day.bind(on_release=self.change_day)
            self.add_widget(day)

    def change_day(self, *args):
        _id = args[0].id
        self.day = _id
        self.app.selected_date = self.app.selected_date.replace(day=self.day)

        # TODO ZNALEŹĆ SPOSÓB NA ODŚWIERZENIE WIDOKU
        DatePicker.refresh


class TimePicker(GridLayout):
    def __init__(self, time_value=time, **kwargs):
        super(TimePicker, self).__init__(**kwargs)
        ...


if __name__ == '__main__':
    class MyApp(App):
        def build(self):
            return DatePicker()


    MyApp().run()
