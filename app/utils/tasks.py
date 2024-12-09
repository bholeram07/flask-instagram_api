from flask import render_template, current_app
from flask_mail import Message
from app.extensions import mail
import os


def send_mail(recipient, html_message, subject):
    """Send an email using Flask-Mail."""
    msg = Message(
        subject=subject,
        recipients=[recipient],
        html=html_message,
        sender=current_app.config.get("MAIL_DEFAULT_SENDER"),
    )
    mail.send(msg)
