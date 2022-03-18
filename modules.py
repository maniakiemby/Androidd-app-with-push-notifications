from datetime import datetime, date, time, timezone
from typing import Type

from dateutil.relativedelta import relativedelta
import calendar

# from kivy.uix.modalview import ModalView
# from kivy.uix.textinput import TextInput
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty

from my_uix import (CalendarButtonDay,
                    TitleCurrentDateWidget,
                    SelectorMonthsWidget,
                    CalendarLayoutWidget,
                    SelectorMonthsButtonPrevious,
                    SelectorMonthsButtonNext,
                    SelectorMonthsLabel,
                    ButtonToday,
                    TimeInput,
                    CancelButtonDate,
                    CancelButtonTime,
                    EnteringTimeBox,
                    CancelContentChangesButton
                    )

Builder.load_file('pickers.kv')


def cancel(*args):
    app = App.get_running_app()
    app.save_data = False
    app.popup.dismiss()


class DatePicker(GridLayout):
    def __init__(self, date_value=date.today(), **kwargs):
        super(DatePicker, self).__init__(**kwargs)
        # self.rows = 5
        self.selected_date = date_value

        self.head = TitleCurrentDateWidget()
        head_date = self.head_date_format()
        self.head_label = Label(text=head_date, font_size=21)
        self.head.add_widget(self.head_label)
        self.today = ButtonToday(text='dziś', on_release=self.set_today)
        self.head.add_widget(self.today)
        self.cancel_button = CancelButtonDate(text="Anuluj", on_release=cancel)
        self.head.add_widget(self.cancel_button)
        self.add_widget(self.head)

        self.selector_months_widget = SelectorMonthsWidget()
        selected_month_str = self.month_format()
        self.selector_months_label = SelectorMonthsLabel(text=selected_month_str)
        self.selector_months_widget.add_widget(self.selector_months_label)
        self.selector_months_widget.add_widget(
            SelectorMonthsButtonPrevious(on_press=self.go_previous_month)
        )
        self.selector_months_widget.add_widget(
            SelectorMonthsButtonNext(on_press=self.go_next_month)
        )
        self.add_widget(self.selector_months_widget)

        self.calendar_days = self.display_calendar()
        self.add_widget(self.calendar_days)

    def head_date_format(self):
        return self.selected_date.strftime('%d/%m/%Y')

    def set_today(self, *args):
        self.clear_widgets()
        self.__init__()

    def month_format(self):
        month_names = ['Styczeń',
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
        _format = '{} {}'.format(month_names[self.selected_date.month - 1], self.selected_date.year)

        return _format

    def display_calendar(self):
        calendar_days = CalendarLayoutWidget()
        days = ['Pon', 'Wt', 'Śr', 'Czw', 'Pt', 'So', 'Nd']
        for day in days:
            name_of_the_day = Label(text=day)
            calendar_days.add_widget(name_of_the_day)

        monthrange = calendar.monthrange(self.selected_date.year, self.selected_date.month)
        first_day_month = monthrange[0]
        days_in_month = monthrange[1]

        _id = 0
        for number in range(days_in_month):
            while first_day_month > _id:
                day = Label(text='')
                calendar_days.add_widget(day)
                _id += 1
            day = CalendarButtonDay(text=str(number + 1), index=(number + 1))
            day.bind(on_release=self.change_date)
            calendar_days.add_widget(day)

        return calendar_days

    def go_previous_month(self, *args):
        self.selected_date = self.selected_date + relativedelta(months=-1)
        self.refresh_month()

    def go_next_month(self, *args):
        self.selected_date = self.selected_date + relativedelta(months=+1)
        self.refresh_month()

    def change_date(self, *args):
        day = args[0].id
        self.selected_date = self.selected_date + relativedelta(day=day)

        head_date = self.head_date_format()
        self.head_label.text = head_date

    def refresh_month(self):
        selected_month_str = self.month_format()
        self.selector_months_label.text = selected_month_str

        self.remove_widget(self.calendar_days)
        self.calendar_days = self.display_calendar()
        self.add_widget(self.calendar_days)


class TimePicker(GridLayout):
    def __init__(self, time_value=datetime.now(), **kwargs):
        super(TimePicker, self).__init__(**kwargs)
        self.time_value = time_value.strftime('%H:%M')
        self.hour = self.time_value[:2]
        self.minute = self.time_value[3:]

        self.cancel_button = CancelButtonTime(on_release=cancel)
        self.add_widget(self.cancel_button)
        self.entering = EnteringTimeBox()
        self.entered_hour = TimeInput(text='')
        self.entered_minute = TimeInput(text='')
        self.entering.add_widget(self.entered_hour)
        self.entering.add_widget(Label(text=':', font_size=60))
        self.entering.add_widget(self.entered_minute)
        self.add_widget(self.entering)


class ContentChanges(GridLayout):
    def __init__(self, text, **kwargs):
        super(ContentChanges, self).__init__(**kwargs)
        self.rows = 2
        self.text = text

        self.cancel_button = CancelContentChangesButton(on_release=cancel)
        self.add_widget(self.cancel_button)
        self.text_input = TextInput(text=self.text)
        self.add_widget(self.text_input)


if __name__ == '__main__':
    class MyApp(App):
        def build(self):
            return DatePicker()


    MyApp().run()
