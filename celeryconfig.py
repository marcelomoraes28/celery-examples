#!/usr/bin/python
from celery.schedules import crontab

broker_url = 'redis://localhost'
result_backend = 'redis://localhost'
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'UTC'
enable_utc = True

# Config the tasks for each story in different queue
task_routes = {
    'story_1_transmit_message': {'queue': 'starwars'},
    'story_1_send_messages': {'queue': 'starwars'},
    'story_2_transmit_message': {'queue': 'alien'},
    'story_2_send_messages': {'queue': 'alien'},
    'relay_messages': {'queue': 'alien'}
}

# Schedule the task relay_messages to run every 3 minutes
beat_schedule = {
    'every-three-minute': {
        'task': 'relay_messages',
        'schedule': crontab(minute='*/3')
    },
}
