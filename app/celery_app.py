from celery import Celery
from celery.schedules import crontab
celery_app = Celery('tasks', broker='redis://localhost:6379/0',
                    CELERY_RESULT_BACKEND='redis://localhost:6379/0')


celery_app.conf.beat_schedule = {
    'delete-old-posts-every-day': {
        'task': 'app.tasks.hard_delete_old_posts',
        'schedule': crontab(minute='*'),  # Runs at 12:00 AM every day
    },
}


celery_app.conf.timezone = 'UTC'
