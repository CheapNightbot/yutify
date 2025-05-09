from flask import render_template, current_app
from app.email import send_email


def send_password_reset_email(user):
    token = user.get_reset_password_token(expires_in=600)
    send_email(
        "[yutify] Reset Your Password",
        sender=current_app.config["ADMIN_EMAIL"],
        recipients=[user.email],
        text_body=render_template("email/reset_password.txt", user=user, token=token, valid_for="10 minutes"),
        html_body=render_template("email/reset_password.html", user=user, token=token, valid_for="10 minutes"),
    )
