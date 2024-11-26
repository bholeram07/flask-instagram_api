from app import create_app,make_celery
app = create_app()
celery=make_celery(app)
if __name__ == "main":
    celery.start()