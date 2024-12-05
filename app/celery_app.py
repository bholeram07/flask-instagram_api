from celery import Celery

celery = Celery()


def init_celery(app):
    celery.conf.update(app.config)
    celery.app = app
