from celery import Celery
from celery.schedules import crontab
celery_app = Celery('tasks', broker='redis://localhost:6379/0',
                    CELERY_RESULT_BACKEND='redis://localhost:6379/0')


celery_app.conf.beat_schedule = {
    'delete-old-posts-every-day': {
        'task': 'tasks.hard_delete_old_posts',
        'schedule': crontab(hour=0, minute=0),  # Runs at 12:00 AM every day
    },
}


celery_app.conf.timezone = 'UTC'
