"""
3PM - so you too can leave the office every day by 3pm!

Copyright (C) 2018 Chris Scheingraber

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import json
from os.path import join, exists
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.properties import ListProperty, StringProperty, \
        NumericProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
import notification
from kivy.uix.settings import SettingsWithTabbedPanel
from settings_info import timer_settings_json, ebs_settings_json
import random

__version__ = '0.6.0'


class MutableTextInput(FloatLayout):
    text = StringProperty()
    multiline = BooleanProperty(True)

    def __init__(self, **kwargs):
        super(MutableTextInput, self).__init__(**kwargs)
        Clock.schedule_once(self.prepare, 0)

    def prepare(self, *args):
        self.w_textinput = self.ids.w_textinput.__self__
        self.w_label = self.ids.w_label.__self__
        self.view()

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and touch.is_double_tap:
            self.edit()
        return super(MutableTextInput, self).on_touch_down(touch)

    def edit(self):
        self.clear_widgets()
        self.add_widget(self.w_textinput)
        self.w_textinput.focus = True

    def view(self):
        self.clear_widgets()
        if not self.text:
            self.w_label.text = "Double tap/click to edit"
        self.add_widget(self.w_label)

    def check_focus_and_view(self, textinput):
        if not textinput.focus:
            self.text = textinput.text
            self.view()


class ProjectView(Screen):
    project_index = NumericProperty()
    project_title = StringProperty()
    project_content = StringProperty()
    project_logged = NumericProperty()
    project_estimated = NumericProperty()
    project_quartiles = StringProperty()


class ProjectViewSimple(Screen):
    project_index = NumericProperty()
    project_title = StringProperty()
    project_content = StringProperty()


class QuickView(Screen):
    project_content = StringProperty()


class ProjectListItem(BoxLayout):
    def __init__(self, **kwargs):
        # print(kwargs)
        del kwargs['index']
        super(ProjectListItem, self).__init__(**kwargs)
    project_content = StringProperty()
    project_title = StringProperty()
    project_index = NumericProperty()
    project_logged = NumericProperty()
    project_estimated = NumericProperty()
    project_progress = StringProperty()


class Projects(Screen):
    data = ListProperty()

    def __init__(self, name, config):
        super(Projects, self).__init__(name=name)
        self.use_ebs = config.get('ebs', 'use_ebs') == '1'

    def args_converter(self, row_index, item):
        if self.use_ebs:
            project_progress_str = '%.f%% (%i/%i)' % (item['logged']*100./item['estimated'], item['logged'], item['estimated'])
        else:
            project_progress_str = ''

        return {
            'project_index': row_index,
            'project_content': item['content'],
            'project_title': item['title'],
            'project_logged': item['logged'],
            'project_estimated': item['estimated'],
            'project_progress': project_progress_str}


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


class ProjectApp(App):
    def build(self):
        self.title = '3PM'
        # initialize settings
        self.use_kivy_settings = False
        self.settings_cls = SettingsWithTabbedPanel
        # initialize projects
        self.projects = Projects(name='projects', config=self.config)
        self.load_projects()
        # initialize ebs history
        self.velocity_history = []
        self.load_velocity_history()
        # initialize timer
        self.timer = Timer(self.config)
        self.simulation_string = StringProperty()
        # screen management and transition
        self.transition = SlideTransition(duration=.35)
        root = ScreenManager(transition=self.transition)
        root.add_widget(self.projects)
        return root

    def build_config(self, config):
        config.setdefaults(
            'timer', {'start_sound': 1,
                      'end_sound': 1,
                      'notification': 1,
                      'notification_timeout': 10,
                      'session_length': 25})
        config.setdefaults(
            'ebs',      {'use_ebs': 1,
                         'number_history': 50})

    def build_settings(self, settings):
        settings.add_json_panel('Timer',
                                self.config,
                                data=timer_settings_json)
        settings.add_json_panel('Simulation',
                                self.config,
                                data=ebs_settings_json)

    def on_config_change(self, config, section, key, value):
        # reinitialize timer
        self.timer.init(config)
        # reinitialize projects
        self.projects = Projects(name='projects', config=config)
        self.load_projects()
        # update projects view config
        self.projects.use_ebs = config.get('ebs', 'use_ebs') == '1'
        self.root.remove_widget(self.root.get_screen('projects'))
        self.root.add_widget(self.projects)
        self.root.current = 'projects'

    def load_velocity_history(self):
        # load velocity history from file
        if exists(self.velocity_history_fn):
            with open(self.velocity_history_fn) as fd:
                self.velocity_history = json.load(fd)
        else:
            # assume bad estimation
            self.velocity_history = [1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7, 8.8, 9.9]

    def save_velocity_history(self):
        # save velocity history to file
        with open(self.velocity_history_fn, 'w') as fd:
            json.dump(self.velocity_history, fd)

    def load_projects(self):
        # load projects from file
        if not exists(self.projects_fn):
            return
        with open(self.projects_fn) as fd:
            data = json.load(fd)
        self.projects.data = data

    def save_projects(self):
        # save projects to file
        with open(self.projects_fn, 'w') as fd:
            json.dump(self.projects.data, fd)

    def delete_project(self, project_index):
        # go to project list
        self.go_projects(project_index)
        # delete project
        del self.projects.data[project_index]
        self.save_projects()
        self.refresh_projects()

    def finish_project(self, project_index):
        # go to project list
        self.go_projects(project_index)
        if self.config.get('ebs', 'use_ebs') == '1':
            # get velocity rating
            vel_rating = self.projects.data[project_index]['logged'] / self.projects.data[project_index]['estimated']
            if vel_rating > 0:
                # save velocity rating to history
                self.velocity_history.append(vel_rating)
                self.save_velocity_history()
        # delete project
        del self.projects.data[project_index]
        self.save_projects()
        self.refresh_projects()

    def edit_project(self, project_index):
        project = self.projects.data[project_index]
        name = 'project{}'.format(project_index)

        if self.root.has_screen(name):
            self.root.remove_widget(self.root.get_screen(name))

        if self.config.get('ebs', 'use_ebs') == '1':
            view = ProjectView(name=name,
                               project_index=project_index,
                               project_title=project.get('title'),
                               project_content=project.get('content'),
                               project_estimated=project.get('estimated'),
                               project_logged=project.get('logged'))

        else:
            view = ProjectViewSimple(name=name,
                                     project_index=project_index,
                                     project_title=project.get('title'),
                                     project_content=project.get('content'))

        self.root.add_widget(view)
        self.transition.direction = 'left'
        self.root.current = view.name
        # update timer logged view
        self.timer.update_logged_string(project.get('logged'))
        # update simulation string
        self.update_simulation_string(project_index)

    def quick_session(self):
        # remove previous quick view screen
        if self.root.has_screen(""):
            self.root.remove_widget(self.root.get_screen(""))
        view = QuickView(project_content="")
        self.root.add_widget(view)
        self.transition.direction = 'left'
        self.root.current = view.name
        self.start_timer()

    def add_project(self):
        self.projects.data.append({'title': 'Unnamed Task', 'content': '', 'logged': 0, 'estimated': 1})
        project_index = len(self.projects.data) - 1
        self.edit_project(project_index)

    def set_project_content(self, project_index, project_content):
        self.projects.data[project_index]['content'] = project_content
        data = self.projects.data
        self.projects.data = []
        self.projects.data = data
        self.save_projects()
        self.refresh_projects()

    def set_project_title(self, project_index, project_title):
        self.projects.data[project_index]['title'] = project_title
        self.save_projects()
        self.refresh_projects()

    def set_project_estimated(self, project_index, estimated):
        new_estimate = float(estimated)
        # sanity check
        if not new_estimate > 0:
            new_estimate = 1.0
        # save new estimate to project
        self.projects.data[project_index]['estimated'] = new_estimate
        self.save_projects()
        self.refresh_projects()
        # update simulation string
        self.update_simulation_string(project_index)

    def set_project_logged(self, project_index, logged):
        self.projects.data[project_index]['logged'] = float(logged)
        self.save_projects()
        self.refresh_projects()

    def refresh_projects(self):
        data = self.projects.data
        self.projects.data = []
        self.projects.data = data

    def go_projects(self, project_index):
        # stop in- or decrementing time
        Clock.unschedule(self.increment_time)
        Clock.unschedule(self.decrement_time)
        if project_index == -1:
            # quick session view; stop timer
            self.stop_timer()
        else:
            # project view; log work and stop timer
            if self.timer.running_down:
                self.stop_work(project_index)
        # go to project view
        self.transition.direction = 'right'
        self.root.current = 'projects'

    def start_work(self, project_index):
        # start new session if timer completely stopped
        if not self.timer.running_down and not self.timer.running_up:
            # start timer
            self.start_timer()
            # set current project index
            self.current_project_index = project_index

        # or reset and start new session if timer runs up
        if self.timer.running_up:
            # stop counting up
            self.stop_timer()
            # start timer
            self.start_timer()

    def stop_work(self, project_index):
        # only log work when timer running down
        if self.timer.running_down:
            if not project_index == -1:
                # log work
                self.log_work(project_index)
                # save log
                self.refresh_projects()
                self.save_projects()
        # stop timer
        self.stop_timer()

    def log_work(self, project_index):
        # get logged fractional unit: (full session time - remaining time) /  full session time
        full_session_time = float(self.config.get('timer', 'session_length'))
        logged_new = (full_session_time * 60. - (self.timer.minutes * 60. + self.timer.seconds)) / \
                     (full_session_time * 60.)
        logged_total = self.projects.data[project_index]['logged'] + logged_new
        # update logged
        self.set_project_logged(project_index, logged_total)
        # update logged view
        self.timer.update_logged_string(logged_total)
        # update simulation view
        self.update_simulation_string(project_index)

    def start_timer(self):
        # stop in- or decrementing time
        Clock.unschedule(self.increment_time)
        Clock.unschedule(self.decrement_time)
        # start decrementing time
        Clock.schedule_interval(self.decrement_time, 1)
        # store flags that timer is running down
        self.timer.running_up = False
        self.timer.running_down = True
        # play start sound if file found
        if self.timer.start_sound_activated and self.timer.start_sound:
            self.timer.start_sound.play()

    def stop_timer(self):
        # stop in- or decrementing time
        Clock.unschedule(self.increment_time)
        Clock.unschedule(self.decrement_time)
        # store flag that timer is not running down or up
        self.timer.running_down = False
        self.timer.running_up = False
        # reinitialize timer
        self.timer.minutes = self.timer.session_length
        self.timer.seconds = 0
        self.timer.update_time_string()

    def decrement_time(self, interval):
        # decrement time of timer
        self.timer.seconds -= 1
        if self.timer.seconds < 0:
            self.timer.minutes -= 1
            self.timer.seconds = 59
        if self.timer.minutes < 0:
            self.timer_alarm()
        self.timer.update_time_string()

    def increment_time(self, interval):
        # increment time of timer
        self.timer.seconds += 1
        if self.timer.seconds > 60:
            self.timer.minutes += 1
            self.timer.seconds = 0
        self.timer.update_time_string()

    def timer_alarm(self):
        # stop decrementing time
        Clock.unschedule(self.decrement_time)
        # set timer to 0:00
        self.timer.minutes = 0
        self.timer.seconds = 0
        # update time string
        self.timer.update_time_string()
        # log work
        self.log_work(self.current_project_index)
        # save log
        self.refresh_projects()
        self.save_projects()
        # store flags that timer is not running down but up
        self.timer.running_down = False
        self.timer.running_up = True
        # start incrementing time
        Clock.schedule_interval(self.increment_time, 1)
        # show notification
        if self.timer.notification_activated:
            self.timer.notification_wrapper.notify(title="3PM", message="Session finished!",
                                                   timeout=self.timer.notification_timeout)
        # play alarm sound if file found
        if self.timer.start_sound_activated and self.timer.alarm_sound:
            self.timer.alarm_sound.play()

    def simulate_completion(self, project_index):
        # only use most recent histories
        number_history = int(self.config.get('ebs', 'number_history'))
        if len(self.velocity_history) > number_history:
            velocity_history = self.velocity_history[-number_history:]
        else:
            velocity_history = self.velocity_history
        # MC simulate completion of project
        sessions_needed = []
        for i in range(0, 100):
            # randomly choose a velocity rating
            vel = random.choice(velocity_history)
            # simulate necessity sessions
            sessions_needed.append(vel * self.projects.data[project_index]['estimated'])
        # sort
        sessions_needed = sorted(sessions_needed)
        # pick quartiles
        quartiles = [sessions_needed[i] for i in [24, 49, 74, 99]]
        # calc completion
        logged = float(self.projects.data[project_index]['logged'])
        completion = [logged*100 / quartiles[i] for i in [0, 1, 2, 3]]
        return quartiles, completion

    def update_simulation_string(self, project_index):
        # simulate completion of project
        quartiles, completion = self.simulate_completion(project_index)
        simulation_string = "%.1f/%.1f/%.1f/%.1f\n%i%%/%i%%/%i%%/%i%%" % tuple(quartiles+completion)
        self.timer.update_simulation_string(simulation_string)

    @property
    def projects_fn(self):
        return join(self.user_data_dir, 'projects.json')

    @property
    def velocity_history_fn(self):
        return join(self.user_data_dir, 'velocity_history.json')


if __name__ == '__main__':
    ProjectApp().run()
