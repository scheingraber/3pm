"""
3PM
=====
Python Pomodoro Project Manager - P.P.P.M.- 3PM - so you too can leave the office every day by 3pm!
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
from kivy.uix.label import Label
from kivy.core.audio import SoundLoader

__version__ = '0.3.2'


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


class ProjectListItem(BoxLayout):

    def __init__(self, **kwargs):
        print(kwargs)
        del kwargs['index']
        super(ProjectListItem, self).__init__(**kwargs)
    project_content = StringProperty()
    project_title = StringProperty()
    project_index = NumericProperty()
    project_logged = NumericProperty()
    project_estimated = NumericProperty()


class Projects(Screen):

    data = ListProperty()

    def args_converter(self, row_index, item):
        return {
            'project_index': row_index,
            'project_content': item['content'],
            'project_title': item['title'],
            'project_logged': item['logged'],
            'project_estimated': item['estimated']}


class Timer(Screen):
    minutes = NumericProperty(25)
    seconds = NumericProperty(0)
    timeString = StringProperty()
    alarmSound = SoundLoader.load('data/gong.wav')
    startSound = SoundLoader.load('data/ticktock.wav')

    def __init__(self, **kwargs):
        super(Timer, self).__init__(**kwargs)
        self.update_time_string()

    def decrement_time(self, interval):
        self.seconds -= 1
        if self.seconds < 0:
            self.minutes -= 1
            self.seconds = 59
        if self.minutes < 0:
            self.alarm()
        self.update_time_string()

    def increment_time(self, interval):
        self.seconds += 1
        if self.seconds > 60:
            self.minutes += 1
            self.seconds = 0
        self.update_time_string()

    def start(self):
        # start decrementing time
        Clock.unschedule(self.decrement_time)
        Clock.schedule_interval(self.decrement_time, 1)
        # play start sound if file found
        if self.startSound:
            self.startSound.play()

    def stop(self):
        # stop in- or decrementing time
        # Clock.unschedule(self.increment_time)
        Clock.unschedule(self.decrement_time)
        # reset timer
        self.minutes = 25
        self.seconds = 0
        self.update_time_string()

    def alarm(self):
        # stop decrementing time
        Clock.unschedule(self.decrement_time)
        # reset timer
        self.minutes = 0
        self.seconds = 0
        self.update_time_string()
        # start incrementing time
        # Clock.schedule_interval(self.increment_time, 1)
        # play alarm sound if file found
        if self.alarmSound:
            self.alarmSound.play()

    def update_time_string(self):
        # update string for clock
        self.timeString = str("%i:%02i" % (self.minutes, self.seconds))


class ProjectApp(App):

    def build(self):
        # initialize projects
        self.projects = Projects(name='projects')
        self.load_projects()
        # initialize timer
        self.timer = Timer()

        # screen management and transition
        self.transition = SlideTransition(duration=.35)
        root = ScreenManager(transition=self.transition)
        root.add_widget(self.projects)
        return root

    def load_projects(self):
        if not exists(self.projects_fn):
            return
        with open(self.projects_fn) as fd:
            data = json.load(fd)
        self.projects.data = data

    def save_projects(self):
        with open(self.projects_fn, 'w') as fd:
            json.dump(self.projects.data, fd)

    def del_project(self, project_index):
        self.go_projects(project_index)
        del self.projects.data[project_index]
        self.save_projects()
        self.refresh_projects()

    def edit_project(self, project_index):
        project = self.projects.data[project_index]
        name = 'project{}'.format(project_index)

        if self.root.has_screen(name):
            self.root.remove_widget(self.root.get_screen(name))

        view = ProjectView(
            name=name,
            project_index=project_index,
            project_title=project.get('title'),
            project_content=project.get('content'),
            project_estimated=project.get('estimated'),
            project_logged=project.get('logged'))

        self.root.add_widget(view)
        self.transition.direction = 'left'
        self.root.current = view.name

    def add_project(self):
        self.projects.data.append({'title': 'NewProject', 'content': '', 'logged': 0, 'estimated': 1})
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

    def set_project_logged(self, project_index, logged):
        self.projects.data[project_index]['logged'] = float(logged)
        self.save_projects()
        self.refresh_projects()

    def set_project_estimated(self, project_index, estimated):
        self.projects.data[project_index]['estimated'] = float(estimated)
        self.save_projects()
        self.refresh_projects()

    def refresh_projects(self):
        data = self.projects.data
        self.projects.data = []
        self.projects.data = data

    def go_projects(self, project_index):
        self.stop_work(project_index)
        self.transition.direction = 'right'
        self.root.current = 'projects'

    def start_work(self, project_index):
        # start timer
        self.timer.start()

    def stop_work(self, project_index):
        # log work
        self.log_work(project_index)
        # stop timer
        self.timer.stop()
        # save log
        self.refresh_projects()
        self.save_projects()

    def log_work(self, project_index):
        # get logged fractional unit: (full session time - remaining time) /  full session time
        logged_new = (25*60. - (self.timer.minutes * 60. + self.timer.seconds)) / (25*60.)
        logged_total = self.projects.data[project_index]['logged'] + logged_new
        # update logged
        self.set_project_logged(project_index, logged_total)

    @property
    def projects_fn(self):
        return join(self.user_data_dir, 'projects.json')


if __name__ == '__main__':
    ProjectApp().run()
