from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings



def send_verification_email(user, code):

    html_message = render_to_string(
        "core/account_activation_email.html",
        {
            "user": user,
            "verification_code": code,
            "expiry_minutes": 1,
        },
    )

    subject = "Verify your Happstock account"

    email_message = EmailMultiAlternatives(
        subject,
        f"Your verification code is {code}",
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
    )

    email_message.attach_alternative(html_message, "text/html")
    email_message.send()

def send_password_reset_email(user, code):

    html_message = render_to_string(
        "core/password_reset_email.html",
        {
            "user": user,
            "code": code,
        },
    )

    subject = "Password Reset Code"

    email_message = EmailMultiAlternatives(
        subject,
        f"Your password reset code is {code}",
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
    )

    email_message.attach_alternative(html_message, "text/html")
    email_message.send()