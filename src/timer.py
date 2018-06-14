from kivy.core.audio import SoundLoader
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen

import notification


class Timer(Screen):
    time_string = StringProperty()
    logged_string = StringProperty()
    simulation_string = StringProperty()

    def __init__(self, config, **kwargs):
        super(Timer, self).__init__(**kwargs)
        # init settings and timer
        self.init(config)
        self.alarm_sound = SoundLoader.load('data/gong.wav')
        self.start_sound = SoundLoader.load('data/ticktock.wav')
        self.running_down = False
        self.running_up = False
        # init notification wrapper
        self.notification_wrapper = notification.Notification()
        # display time string
        self.update_time_string()

    def init(self, config):
        # update sound and notification
        self.start_sound_activated = config.get('timer', 'start_sound') == '1'
        self.end_sound_activated = config.get('timer', 'end_sound') == '1'
        self.vibration_activated = config.get('timer', 'vibrate') == '1'
        self.notification_activated = config.get('timer', 'notification') == '1'
        self.notification_timeout = float(config.get('timer', 'notification_timeout'))
        # update session length
        self.session_length = float(config.get('timer', 'session_length'))
        # initialize timer
        self.minutes = self.session_length
        self.seconds = 0
        # update display
        self.update_time_string()

    def update_time_string(self):
        # update string for clock
        self.time_string = "%i:%02i" % (self.minutes, self.seconds)

    def update_logged_string(self, logged):
        # update string for logged view
        self.logged_string = "%.1f" % logged

    def update_simulation_string(self, simulation_string):
        # update string
        self.simulation_string = simulation_string