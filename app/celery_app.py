from celery import Celery
from celery.schedules import crontab
celery_app = Celery('tasks', broker='redis://localhost:6379/0',
                    CELERY_RESULT_BACKEND='redis://localhost:6379/0')


celery_app.conf.beat_schedule = {
    'delete-old-posts-every-day': {
        'task': 'app.tasks.hard_delete_old_posts',
        'schedule': crontab(minute= 0, hour= 0 ),  # Runs at 12:00 AM every day
    },
    'delete-old-story-every-day': {
        'task': 'app.tasks.hard_delete_story',
        # Runs at 12:00 AM every day
        'schedule': crontab(minute=0, hour=0),
    },
    'delete-old-user-every-day':{
    'task': 'app.tasks.hard_delete_user',
    'schedule': crontab(minute=0 , hour=0), # Runs at 12:00 AM every day
},
    'delete-old-comments-every-day': {
        'task': 'app.tasks.hard_delete_comments',
        'schedule': crontab(minute= 0 ,hour= 0),  # Runs at 12:00 AM every day
    
},
    'delete-user-story-every-day': {
        'task': 'app.tasks.hard_delete_story_by_user',
        'schedule': crontab(minute='*'),  # Runs at 12:00 AM every day

    },
}



celery_app.conf.timezone = 'UTC'
