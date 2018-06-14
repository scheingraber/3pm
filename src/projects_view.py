from kivy.clock import Clock
from kivy.properties import ListProperty, StringProperty, BooleanProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen


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


class ProjectViewWithoutNotepad(Screen):
    project_index = NumericProperty()
    project_title = StringProperty()
    project_logged = NumericProperty()
    project_estimated = NumericProperty()
    project_quartiles = StringProperty()


class ProjectViewSimple(Screen):
    project_index = NumericProperty()
    project_title = StringProperty()
    project_content = StringProperty()


class ProjectViewSimpleWithoutNotepad(Screen):
    project_index = NumericProperty()
    project_title = StringProperty()


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