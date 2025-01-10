from flask import render_template, current_app
from flask_mail import Message
from app.extensions import mail
from app.celery_app import celery_app
from datetime import datetime, timedelta
from app.models.post import Post
from app.models.user import User
from app.models.story import Story
from app.models.comment import Comment
from app.models.follow_request import FollowRequest
from app.models.follower import Follow
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

@celery_app.task
def send_location_mail(recipient,html_message):
    from app import create_app
    app = create_app()
    with app.app_context():
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
            db.session.delete(post)  

        # Commit the changes
        db.session.commit()


@celery_app.task
def hard_delete_story():
    """Hard delete posts marked for deletion."""
    from app import create_app
    app = create_app()

    with app.app_context():
        # Get the current time in UTC
        utc_now = datetime.now(pytz.utc)

        # Set the threshold date (1 minute before current time)
        threshold_date = utc_now - timedelta(minutes=1)

        # Fetch posts marked as "soft deleted" and older than 1 minute
        old_story = Story.query.filter(Story.created_at < threshold_date).all() 
        
        

        # Hard delete the posts
        for story in old_story:
            # Assuming you have a delete() method in your model
            db.session.delete(story)

        # Commit the changes
        db.session.commit()


@celery_app.task
def hard_delete_story_by_user():
    """Hard delete posts marked for deletion."""
    from app import create_app
    app = create_app()

    with app.app_context():
        # Get the current time in UTC
        utc_now = datetime.now(pytz.utc)

        # Set the threshold date (1 minute before current time)
        threshold_date = utc_now - timedelta(minutes=1)

        # Fetch posts marked as "soft deleted" and older than 1 minute
        old_story = Story.query.filter_by(is_deleted = False).all()

        # Hard delete the posts
        for story in old_story:
            # Assuming you have a delete() method in your model
            db.session.delete(story)

        # Commit the changes
        db.session.commit()
    
@celery_app.task
def hard_delete_user():
    """Hard delete posts marked for deletion."""
    from app import create_app
    app = create_app()

    with app.app_context():
        # Get the current time in UTC
        utc_now = datetime.now(pytz.utc)

        # Set the threshold date (1 minute before current time)
        threshold_date = utc_now - timedelta(seconds=1)

        # Fetch posts marked as "soft deleted" and older than 1 minute
        deleted_user = User.query.filter(User.deleted_at < threshold_date).all()

        # Hard delete the posts
        for user in deleted_user:
            # Assuming you have a delete() method in your model
            db.session.delete(user)

        # Commit the changes
        db.session.commit()
    

@celery_app.task
def hard_delete_comments():
    """Hard delete posts marked for deletion."""
    from app import create_app
    app = create_app()

    with app.app_context():
        # Get the current time in UTC
        utc_now = datetime.now(pytz.utc)

        # Set the threshold date (1 minute before current time)
        threshold_date = utc_now - timedelta(minutes=1)

        # Fetch posts marked as "soft deleted" and older than 1 minute
        deleted_comments = Comment.query.filter(
            Comment.deleted_at < threshold_date).all()

        # Hard delete the posts
        for comment in deleted_comments:
            # Assuming you have a delete() method in your model
            db.session.delete(comment)

        # Commit the changes
        db.session.commit()
        

@celery_app.task
def hard_delete_user():
    """Hard delete posts marked for deletion."""
    from app import create_app
    app = create_app()

    with app.app_context():
        # Get the current time in UTC
        utc_now = datetime.now(pytz.utc)

        # Set the threshold date (1 minute before current time)
        threshold_date = utc_now - timedelta(seconds=1)

        # Fetch posts marked as "soft deleted" and older than 1 minute
        non_verified_user = User.query.filter_by(is_verified = False).all()

        # Hard delete the posts
        for user in deleted_user:
            # Assuming you have a delete() method in your model
            db.session.delete(user)

        # Commit the changes
        db.session.commit()



# @celery_app.task
# def accept_the_request():
#     """Hard delete posts marked for deletion."""
#     from app import create_app
#     app = create_app()

#     with app.app_context():
#         # Get the current time in UTC
#         utc_now = datetime.now(pytz.utc)

#         # Set the threshold date (1 minute before current time)
#         threshold_date = utc_now - timedelta(minutes=1)

#         # Fetch posts marked as "soft deleted" and older than 1 minute
#         user = User.query.filter(is_private == False).all()
#         followrequests = FollowRequest.query.filter(
#             following_id=self.current_user_id).all()
#         for follower in followrequests:
#             follow = Follow(follower_id=follower.follower_id,following_id=follower.following_id)
#             db.session.add(follow)
#         # Hard delete the posts
      
#         # Commit the changes
#         db.session.commit()
