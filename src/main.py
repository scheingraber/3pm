from kivy.app import App
from kivy.lang import Builder
from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock


class MainWidget(BoxLayout):
    number = NumericProperty()
    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        Clock.schedule_interval(self.increment_time, .1)
        self.increment_time(0)

    def increment_time(self, interval):
        self.number += .1

    def start(self):
        Clock.unschedule(self.increment_time)
        Clock.schedule_interval(self.increment_time, .1)

    def stop(self):
        Clock.unschedule(self.increment_time)

class mainApp(App):
    def build(self):
        return MainWidget()

mainApp().run()
