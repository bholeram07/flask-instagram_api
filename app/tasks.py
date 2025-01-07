from flask import render_template, current_app
from flask_mail import Message
from app.extensions import mail
from app.celery_app import celery_app
from datetime import datetime, timedelta
from app.models.post import Post
from app.extensions import db
import pytz



@celery_app.task
def send_mail(recipient, html_message, subject):
        """Send an email using Flask-Mail."""
        from app import create_app
        app = create_app()
        with app.app_context():
            msg = Message(
                subject=subject,
                recipients=[recipient],
                html=html_message,
                sender=current_app.config.get("MAIL_DEFAULT_SENDER"),
            )
            mail.send(msg)


def send_location_mail(recipient,html_message):
    
    msg = Message(
        subject="Login found",
        recipients=[recipient],
        html=html_message,
        sender=current_app.config.get("MAIL_DEFAULT_SENDER"),
    )
    mail.send(msg)
    
    
@celery_app.task
def hard_delete_old_posts():
    """Hard delete posts marked for deletion."""
    from app import create_app
    app = create_app()

    with app.app_context():
        # Get the current time in UTC
        utc_now = datetime.now(pytz.utc)

        # Set the threshold date (1 minute before current time)
        threshold_date = utc_now - timedelta(minutes=1)

        # Fetch posts marked as "soft deleted" and older than 1 minute
        old_posts = Post.query.filter(
            Post.is_deleted == True, Post.deleted_at < threshold_date).all()

        # Hard delete the posts
        for post in old_posts:
            db.session.delete(post)  # Assuming you have a delete() method in your model

        # Commit the changes
        db.session.commit()
