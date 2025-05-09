from threading import Thread

from flask import current_app
from flask_mail import Message
from flask_security import MailUtil

from app.extensions import mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


class MyMailUtil(MailUtil):
    def send_mail(self, template, subject, recipient, sender, body, html, **kwargs):
        # In Flask-Mail, sender can be a two element tuple -- (name, address)
        if isinstance(sender, tuple) and len(sender) == 2:
            sender = (str(sender[0]), str(sender[1]))
        else:
            sender = str(sender)
        msg = Message(subject=subject, sender=sender, recipients=[recipient])
        msg.body = body
        msg.html = html

        Thread(
            target=send_async_email, args=(current_app._get_current_object(), msg)
        ).start()
