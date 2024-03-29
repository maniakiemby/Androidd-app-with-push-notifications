from typing import Union, Type
from datetime import datetime, date, time, timezone
import re
from dateutil.relativedelta import relativedelta
import calendar
from abc import ABC, abstractmethod

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.modalview import ModalView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.layout import Layout
from kivy.properties import ObjectProperty
from kivy.core.window import Window

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
                    ButtonBack,
                    ContentInput,
                    ButtonConfirm,
                    ErrorMessage,
                    )

# Builder.load_file('pickers.kv')


# TODO: Stworzyć jedną klasę abstrakcyjną do widoków tasks i expenses z przyciskami
#  i z niej dziedziczyć na konkretne widoki
#  ulepszyć obiektowo również pobieranie daty i czasu wykonania zadania


def cancel(*args):
    app = App.get_running_app()
    app.save_data = False
    app.popup.dismiss()


class TaskLayout(GridLayout):
    def __init__(self, **kwargs):
        super(TaskLayout, self).__init__(**kwargs)
        self.ids['button_back'].bind(on_release=self.back)
        self.ids['button_confirm'].bind(on_release=self.confirm)

        self.content_input = self.ids['content_input']
        self.content_input.bind(on_text_validate=self.confirm)

        self.task_date_of_performance = self.ids['task_date']
        self.task_date_of_performance.bind(on_release=self.open_date_picker)
        self.task_time_of_performance = self.ids['task_time']
        self.task_time_of_performance.bind(one_release=self.open_time_picker())

        self.button_change_background_color = self.ids['change_background_color']
        self.button_change_background_color.bind(on_release=self.open_color_picker)

        self.button_change_font_color = self.ids['change_font_color']
        self.button_change_font_color.bind(on_release=self.open_color_picker)

    @staticmethod
    @abstractmethod
    def back(*args):
        pass

    def confirm(self, *args):
        if self.fields_filled():
            self.on_confirm()

    def open_date_picker(self, *args):
        _date = self.task_date_of_performance.text
        if _date:
            date_picker = DatePicker(_date)
        else:
            date_picker = DatePicker()

        app = App.get_running_app()
        app.popup = ModalView(size_hint=(None, None),
                              size=(Window.width - 25, Window.height / 1.7),
                              auto_dismiss=True,
                              on_dismiss=self.grab_date
                              )
        app.popup.add_widget(date_picker)
        app.save_data = True
        app.popup.open()

    def grab_date_from_datepicker(self, *args):
        app = App.get_running_app()
        if app.save_data:
            self.task_date_of_performance.text = app.popup.date_picker.selected_date

    def open_time_picker(self, *args):
        _time = self.task_time_of_performance.text
        if _time:
            time_picker = TimePicker(_time)
        else:
            time_picker = TimePicker()
        app = App.get_running_app()
        app.popup = ModalView(size_hint=(None, None),
                              pos_hint={'top': .9},
                              size=(Window.width / 1.5, Window.height / 3),
                              auto_dismiss=True,
                              on_dismiss=self.grab_time
                              )
        app.popup.add_widget(time_picker)
        app.save_data = True
        app.popup.open()

    def grab_time_from_timepicker(self, *args):
        app = App.get_running_app()
        if app.save_data:
            hour = app.popup.time_picker.entered_hour
            minute = app.popup.time_picker.entered_minute
            if not hour or minute:
                return
            if len(hour) == 1:
                hour = '0' + hour
            if len(minute) == 1:
                minute = '0' + minute
            task_time = hour + ':' + minute

            try:
                task_time = time.fromisoformat(task_time)
            except ValueError:
                popup = ErrorMessage()
                popup.message_content.text = "Wprowadź poprawną godzinę\nw formacie 24h:60m"
            else:
                self.task_time_of_performance.text = task_time.isoformat()

    def open_color_picker(self, *args):
        pass

    def fields_filled(self):
        essence = self.content_input.text
        if essence != '':
            return True

    def clear_the_fields(self):
        # set default color background
        # set default color font
        self.content_input.text = ''
        self.task_date_of_performance = 'Dodaj datę'
        self.task_time_of_performance = 'Dodaj czas'

    @abstractmethod
    def on_confirm(self):
        pass


class SideView(GridLayout):
    def __init__(self, **kwargs):
        super(SideView, self).__init__(**kwargs)


class DatePicker(GridLayout):
    def __init__(self, date_value=date.today(), **kwargs):
        super(DatePicker, self).__init__(**kwargs)
        self.selected_date = date_value

        self.head = TitleCurrentDateWidget()
        head_date = self.head_date_format()
        self.head_label = Label(text=head_date, font_size=100)
        self.head.add_widget(self.head_label)
        self.today = ButtonToday(on_release=self.set_today)
        self.head.add_widget(self.today)
        self.cancel_button = CancelButtonDate(on_release=cancel)
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


def list_of_categories():
    with open('categories_of_expenses.txt', 'r', encoding='UTF-8') as f:
        values = f.readlines()

    return [category.strip() for category in values]


class NewExpense:
    def __init__(self):
        self.index = None
        self.expense = None
        self.category_id = None
        self.matter = None
        self.date_add = datetime.now().date().isoformat()


class ExpenseLayout(GridLayout):
    def __init__(self, **kwargs):
        super(ExpenseLayout, self).__init__(**kwargs)
        self.date_add = datetime.now().date().isoformat()
        self.expense_field = self.ids['expense']
        self.matter_field = self.ids['matter']
        self.button_date_add = self.ids['date_add']
        self.button_date_add.text = self.date_add
        self.date_picker = None
        # self.button_cancel = self.ids['cancel']
        # self.button_confirm = self.ids['confirm']

        self.categories = list_of_categories()
        self.category_selector = self.ids['category']
        self.dropdown = DropDown()
        for category in self.categories:
            self.button_category = Button(text=category, size_hint=(1, None), height=150)
            self.button_category.bind(on_release=lambda button_category: self.dropdown.select(button_category.text))
            self.dropdown.add_widget(self.button_category)
        self.category_selector.bind(on_release=self.dropdown.open)
        self.category_selector.auto_width = False
        self.dropdown.bind(on_select=lambda instance, x: setattr(self.category_selector, 'text', x))

    def open_date_picker(self):
        the_set_date = self.button_date_add.text
        if the_set_date:
            self.date_picker = DatePicker(date.fromisoformat(the_set_date))
        else:
            self.date_picker = DatePicker()
        app = App.get_running_app()
        app.popup = ModalView(size_hint=(None, None),
                              size=(Window.width - 25, Window.height / 1.7),
                              auto_dismiss=True,
                              on_dismiss=self.grab_date
                              )
        app.popup.add_widget(self.date_picker)
        app.save_data = True
        app.popup.open()

    def grab_date(self, *args):
        app = App.get_running_app()
        if app.save_data:
            self.date_add = self.date_picker.selected_date.isoformat()
            self.button_date_add.text = self.date_add

    def data_complete(self) -> bool:
        if self.category_selector.text == 'wybierz kategorię' or self.expense_field.text == '':
            self.error_data_not_complete()
            return False
        return True

    def amount_money_correctly(self) -> bool:
        expense = self.expense_field.text.strip()
        if re.search(',', expense):
            expense = expense.replace(',', '.')
        # below I check whether the number represents the amount of money
        search_amount_of_money = re.search('^\d+$|^[0-9]*\.[0-9]{1,2}$', expense)
        if search_amount_of_money:
            self.expense_field.text = expense
            return True
        else:
            self.error_amount_money_not_correctly()
            return False

    def clear_the_fields(self):
        self.expense_field.text = ''
        self.dropdown.select('wybierz kategorię')  # this string must too same in .kv file under id: category
        self.matter_field.text = ''
        self.button_date_add.text = self.date_add

    @staticmethod
    def error_data_not_complete():
        popup = ErrorMessage()
        popup.message_content.text = "Wpis nie jest zupełny."

    @staticmethod
    def error_amount_money_not_correctly():
        popup = ErrorMessage()
        popup.message_content.text = "Podano złą wartość w polu z kwotą wydatków."


if __name__ == '__main__':
    class MyApp(App):
        def build(self):
            return DatePicker()


    MyApp().run()
