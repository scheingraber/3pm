import json

# default settings for 3PM
session_settings_json = json.dumps([
    {'type': 'title',
     'title': 'Sounds'},
    {'type': 'bool',
     'title': 'Session Start Sound',
     'desc': 'Play tik-tok sound when beginning a session',
     'section': 'sessions',
     'key': 'start_sound'},
    {'type': 'bool',
     'title': 'Session End Sound',
     'desc': 'Play ding-dong sound when a session ends',
     'section': 'sessions',
     'key': 'end_sound'},
    {'type': 'title',
     'title': 'Notifications'},
    {'type': 'bool',
     'title': 'Session End Notification',
     'desc': 'Show notification when a session ends',
     'section': 'sessions',
     'key': 'notification'},
    {'type': 'title',
     'title': 'Timer'},
    {'type': 'numeric',
     'title': 'Session Length',
     'desc': 'Session interval length in minutes',
     'section': 'sessions',
     'key': 'session_length'}])

ebs_settings_json = json.dumps([
    {'type': 'title',
     'title': 'History'},
    {'type': 'bool',
     'title': 'Log Velocity Ratings',
     'desc': 'Keep Velocity Ratings for Evidence-Based Scheduling',
     'section': 'ebs',
     'key': 'keep_velocity_ratings'}])
