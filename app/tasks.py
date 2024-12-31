from flask import render_template, current_app
from flask_mail import Message
from app.extensions import mail
from app.celery_app import celery_app



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
    from app.models import Post  # Adjust based on your model location
    from datetime import datetime, timedelta

    app = create_app()

    with app.app_context():
        # Fetch posts marked as "soft deleted" and older than 15 days
        threshold_date = datetime.utcnow() - timedelta(days=15)
        old_posts = Post.query.filter(
            Post.is_deleted == True, Post.deleted_at < threshold_date).all()

        # Hard delete the posts
        for post in old_posts:
            post.delete()  # Assuming you have a delete() method in your model
        app.db.session.commit()

    print(f"{len(old_posts)} posts hard deleted.")
    
