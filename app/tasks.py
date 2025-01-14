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
from app.utils.upload_image_or_video import PostImageVideo
from app.utils.upload_story_content import delete_story_from_s3
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
def process_follow_requests(user_id):
    # Import inside the task to avoid circular imports
    from app import create_app
    app=create_app()
    with app.app_context():

        pending_follow_requests = FollowRequest.query.filter_by(
            following_id=user_id).all()
        new_follows = [
            Follow(following_id=user_id, follower_id=request.follower_id)
            for request in pending_follow_requests
        ]
    

        # Bulk insert follows
        db.session.bulk_save_objects(new_follows)
        FollowRequest.query.filter_by(following_id=user_id).delete()
        db.session.commit()


        
    
@celery_app.task
def hard_delete_old_posts():
    """Hard delete posts marked for deletion."""
    from app import create_app
    app = create_app()

    with app.app_context():
        # Get the current time in UTC
        utc_now = datetime.now(pytz.utc)

        # Set the threshold date (1 minute before current time)
        threshold_date = utc_now - timedelta(minutes= 1)

        # Fetch posts marked as "soft deleted" and older than 1 minute
        old_posts = Post.query.filter(
            Post.is_deleted == True, Post.deleted_at < threshold_date).all()

        # Hard delete the posts
        for post in old_posts:
            post_image_video_obj = PostImageVideo(
                post, post.image_or_video, post.user)
            post_image_video_obj.delete_image_or_video()
            
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
            delete_story_from_s3(story)
            db.session.delete(like)
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
        threshold_date = utc_now - timedelta(minutes=2)

        # Fetch posts marked as "soft deleted" and older than 1 minute
        old_story = Story.query.filter(Story.is_deleted == True).all()


        # Hard delete the posts
        for story in old_story:
            # Assuming you have a delete() method in your model
            delete_story_from_s3(story)
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
        threshold_date = utc_now - timedelta(minutes=1)

        # Fetch posts marked as "soft deleted" and older than 1 minute
        deleted_user = User.query.filter(User.deleted_at < threshold_date).all()

        # Hard delete the posts
        for user in deleted_user:
            # Assuming you have a delete() method in your model
            db.session.delete(user)
            db.session.commit()

        # Commit the changes
   
    

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
def hard_delete_non_verified_user():
    """Hard delete posts marked for deletion."""
    from app import create_app
    app = create_app()

    with app.app_context():
        # Get the current time in UTC
        utc_now = datetime.now(pytz.utc)

        # Fetch posts marked as "soft deleted" and older than 1 minute
        threshold_date = utc_now - timedelta(minutes=1)
        non_verified_user = User.query.filter(User.is_verified == False, User.created_at < threshold_date).all()

        # Hard delete the posts
        for user in non_verified_user:
            # Assuming you have a delete() method in your model
            db.session.delete(user)

        # Commit the changes
        db.session.commit()



