from kivy.app import App
from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock


class MainWidget(GridLayout):
    minutes = NumericProperty(35)
    seconds = NumericProperty()
    timeString = StringProperty()

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        Clock.schedule_interval(self.decrement_time, 1)
        self.decrement_time(0)
        self.timeString = str(self.minutes) + ':' + str(self.seconds)

    def decrement_time(self, interval):
        self.seconds -= 1
        if self.seconds < 0:
            self.minutes -= 1
            self.seconds = 59
        self.timeString = str(self.minutes) + ':' + str(self.seconds)

    def start(self):
        Clock.unschedule(self.decrement_time)
        Clock.schedule_interval(self.decrement_time, 1)

    def stop(self):
        self.minutes = 35
        self.seconds = 0
        Clock.unschedule(self.decrement_time)


class MainApp(App):
    def build(self):
        return MainWidget()

MainApp().run()
