import json

# default settings for 3PM
timer_settings_json = json.dumps([
    {'type': 'title',
     'title': 'Sounds'},
    {'type': 'bool',
     'title': 'Session Start Sound',
     'desc': 'Play tik-tok sound when beginning a session',
     'section': 'timer',
     'key': 'start_sound'},
    {'type': 'bool',
     'title': 'Session End Sound',
     'desc': 'Play ding-dong sound when a session ends',
     'section': 'timer',
     'key': 'end_sound'},
    {'type': 'title',
     'title': 'Notifications'},
    {'type': 'bool',
     'title': 'Session End Notification',
     'desc': 'Show notification when a session ends',
     'section': 'timer',
     'key': 'notification'},
    {'type': 'numeric',
     'title': 'Notification Timeout',
     'desc': 'Time notification is visible [in seconds]',
     'section': 'timer',
     'key': 'notification_timeout'},
    {'type': 'title',
     'title': 'Timer'},
    {'type': 'numeric',
     'title': 'Session Length',
     'desc': 'Session interval length [in minutes]',
     'section': 'timer',
     'key': 'session_length'}])

ebs_settings_json = json.dumps([
    {'type': 'bool',
     'title': 'Use Evidence Based Scheduling',
     'desc': 'Show EBS related functionality throughout app',
     'section': 'ebs',
     'key': 'use_ebs'}])
