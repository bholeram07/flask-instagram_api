from flask import render_template, current_app
from flask_mail import Message
from app.extensions import mail  # Ensure you import your `mail` instance correctly
import os


def send_mail(recipient):
    """Send an email using Flask-Mail."""
        # Render the email body from the template
    html_message = render_template('welcome_email.html', 
            # username="Bholeram", 
            # year=2024
        )
    msg = Message(
        subject="Welcome to our app!",
        recipients=[recipient],
        html=html_message,
        sender=current_app.config.get("MAIL_DEFAULT_SENDER"),
    )
    mail.send(msg)
