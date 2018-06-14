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
# need to set kivy configs before importing anything else
from kivy.config import Config
Config.set('kivy', 'exit_on_escape', 0)

# import 3PM classes
from timer import Timer
from projects_view import Projects, ProjectView, ProjectViewWithoutNotepad, ProjectViewSimple,\
                         ProjectViewSimpleWithoutNotepad, QuickView

# third party imports
import json
from os.path import join, exists
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.properties import StringProperty
from kivy.clock import Clock
from kivy.uix.settings import SettingsWithTabbedPanel
from settings_info import timer_settings_json, ebs_settings_json
import random
from kivy.utils import platform
import datetime
if platform == 'android':
    from plyer import vibrator
elif platform == 'win':
    from infi.systray import SysTrayIcon

__version__ = '0.6.4'


class ProjectApp(App):
    def build(self):
        self.title = '3PM'
        # initialize settings
        self.use_kivy_settings = False
        self.settings_cls = SettingsWithTabbedPanel
        self.icon = join('data', 'icon.ico')
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

    def on_start(self):
        # no current project index
        self.current_project_index = -1
        if platform == 'win':
            # initialize system tray
            menu_options = (("Show Session Info", "Show current task and remaining time.", self.systray_show_info),)
            hover_text = "Personal Project Productivity Manager - 3PM"
            self.systray = SysTrayIcon("data/icon.ico", hover_text, menu_options, default_menu_index=0, on_quit=self.systray_close_window)
            self.systray.start()

    def on_stop(self):
        if platform == 'win':
            # shutdown tray icon
            self.systray.shutdown()

    def systray_show_info(self, sysTrayIcon):
        # remaining time
        if self.timer.running_down:
            message_time = '%s remaining!' % self.timer.time_string
        elif self.timer.running_up:
            message_time = 'On break since %s.' % self.timer.time_string
        else:
            message_time = 'No session running.'
        # project string
        if self.current_project_index == -1:
            project_title = 'Quick Session'
        else:
            project_title = self.projects.data[self.current_project_index]['title']
        # show notification
        self.timer.notification_wrapper.notify(title=project_title, message=message_time,
                                               timeout=self.timer.notification_timeout)

    def systray_close_window(self, sysTrayIcon):
        # stop app
        exit(0)

    def build_config(self, config):
        if platform == 'android':
            # android defaults
            config.setdefaults(
                'timer', {'start_sound': 1,
                          'end_sound': 1,
                          'vibrate': 1,
                          'notification': 0,
                          'notification_timeout': 10,
                          'session_length': 25,
                          'hide_window': 0,
                          'use_notepad': 0})
            config.setdefaults(
                'ebs',      {'use_ebs': 1,
                             'number_history': 50,
                             'log_activity': 0})
        else:
            # defaults for desktop computers
            config.setdefaults(
                'timer', {'start_sound': 1,
                          'end_sound': 1,
                          'vibrate': 0,
                          'notification': 1,
                          'notification_timeout': 10,
                          'session_length': 25,
                          'hide_window': 0,
                          'use_notepad': 1})
            config.setdefaults(
                'ebs',      {'use_ebs': 1,
                             'number_history': 50,
                             'log_activity': 0})

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
        self.current_project_index = project_index
        project = self.projects.data[project_index]
        name = 'project{}'.format(project_index)

        if self.root.has_screen(name):
            self.root.remove_widget(self.root.get_screen(name))

        if self.config.get('ebs', 'use_ebs') == '1':
            if self.config.get('timer', 'use_notepad') == '0':
                view = ProjectViewWithoutNotepad(name=name,
                                                 project_index=project_index,
                                                 project_title=project.get('title'),
                                                 project_estimated=project.get('estimated'),
                                                 project_logged=project.get('logged'))
            else:
                view = ProjectView(name=name,
                                   project_index=project_index,
                                   project_title=project.get('title'),
                                   project_content=project.get('content'),
                                   project_estimated=project.get('estimated'),
                                   project_logged=project.get('logged'))

        else:
            if self.config.get('timer', 'use_notepad') == '0':
                view = ProjectViewSimpleWithoutNotepad(name=name,
                                                       project_index=project_index,
                                                       project_title=project.get('title'))
            else:
                view = ProjectViewSimple(name=name,
                                         project_index=project_index,
                                         project_title=project.get('title'),
                                         project_content=project.get('content'))

        # add widget to root
        self.root.add_widget(view)
        self.transition.direction = 'left'
        self.root.current = view.name
        # update timer logged view
        self.timer.update_logged_string(project.get('logged'))
        # update simulation string
        self.update_simulation_string(project_index)

    def quick_session(self):
        if not self.root.current == '':
            # remove previous quick view screen
            if self.root.has_screen(''):
                self.root.remove_widget(self.root.get_screen(''))
            view = QuickView(project_content='')
            self.root.add_widget(view)
            self.transition.direction = 'left'
            self.root.current = view.name
            self.current_project_index = -1
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
        self.current_project_index = -1

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
        # hide main window if option activated
        if platform == 'win' and self.config.get('timer', 'hide_window') == '1':
            self.root_window.hide()

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
        if not self.current_project_index == -1:
            self.log_work(self.current_project_index)
        # save log
        self.refresh_projects()
        self.save_projects()
        if platform == 'win' and self.config.get('timer', 'hide_window') == '1':
            # show main window again - twice to get focus
            self.root_window.show()
            self.root_window.show()

        # log date of completed session to file
        if self.config.get('ebs', 'log_activity') == '1':
            # date and count for this session
            date_today = datetime.datetime.today().strftime('%Y-%m-%d')
            count_today = 1
            # read old file
            if exists(self.activity_fn):
                with open(self.activity_fn, 'r') as f:
                    # read lines
                    lines = f.readlines()
                    # get date and count
                    date_file, count_file = lines[-1].split()
                    if date_file == date_today:
                        # add count from earlier sessions today
                        count_today += int(count_file)
            else:
                lines = []
            # replace last line
            lines = lines[:-1]
            lines.append("%s\t%s\n" % (date_today, str(count_today)))
            # write new file
            with open(self.activity_fn, 'w') as f:
                f.writelines(lines)

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
        # vibrate on android
        if self.timer.vibration_activated and platform == 'android':
            vibrator.vibrate(2)

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
        simulation_string = "%i/%i/%i/%i\n%i%%/%i%%/%i%%/%i%%" % tuple(quartiles+completion)
        self.timer.update_simulation_string(simulation_string)

    @property
    def projects_fn(self):
        return join(self.user_data_dir, 'projects.json')

    @property
    def velocity_history_fn(self):
        return join(self.user_data_dir, 'velocity_history.json')

    @property
    def activity_fn(self):
        return join(self.user_data_dir, 'daily_activity.txt')


if __name__ == '__main__':
    # start app
    ProjectApp().run()
