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

__version__ = '0.1.1'


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


class ProjectListItem(BoxLayout):

    def __init__(self, **kwargs):
        print(kwargs)
        del kwargs['index']
        super(ProjectListItem, self).__init__(**kwargs)
    project_content = StringProperty()
    project_title = StringProperty()
    project_index = NumericProperty()


class Projects(Screen):

    data = ListProperty()

    def args_converter(self, row_index, item):
        return {
            'project_index': row_index,
            'project_content': item['content'],
            'project_title': item['title']}


class Timer(Screen):
    minutes = NumericProperty(25)
    seconds = NumericProperty()
    timeString = StringProperty()

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

    def stop(self):
        # log partial session (if we were in countdown mode)
        # todo
        # reset timer
        self.minutes = 25
        self.seconds = 0
        self.update_time_string()
        # stop in- or decrementing time
        Clock.unschedule(self.increment_time)
        Clock.unschedule(self.decrement_time)

    def alarm(self):
        # stop decrementing time
        Clock.unschedule(self.decrement_time)
        # log work to task
        # todo
        # reset timer
        self.minutes = 0
        self.seconds = 0
        self.update_time_string()
        # start incrementing time
        Clock.schedule_interval(self.increment_time, 1)
        # play alarm sound
        # todo

    def update_time_string(self):
        # update string for clock
        self.timeString = str("%i:%02i" % (self.minutes, self.seconds))


class ProjectApp(App):

    def build(self):
        self.projects = Projects(name='projects')
        self.load_projects()

        self.timer = Timer()

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
        del self.projects.data[project_index]
        self.save_projects()
        self.refresh_projects()
        self.go_projects()

    def edit_project(self, project_index):
        project = self.projects.data[project_index]
        name = 'project{}'.format(project_index)

        if self.root.has_screen(name):
            self.root.remove_widget(self.root.get_screen(name))

        view = ProjectView(
            name=name,
            project_index=project_index,
            project_title=project.get('title'),
            project_content=project.get('content'))

        self.root.add_widget(view)
        self.transition.direction = 'left'
        self.root.current = view.name

    def add_project(self):
        self.projects.data.append({'title': 'New Project', 'content': '', 'logged': '', 'estimated': ''})
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

    def refresh_projects(self):
        data = self.projects.data
        self.projects.data = []
        self.projects.data = data

    def go_projects(self):
        self.transition.direction = 'right'
        self.root.current = 'projects'

    @property
    def projects_fn(self):
        return join(self.user_data_dir, 'projects.json')


if __name__ == '__main__':
    ProjectApp().run()
