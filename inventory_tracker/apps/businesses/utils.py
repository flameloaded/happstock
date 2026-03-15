from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings


def send_business_invitation_email(email, invite_link, business, role):

    html_content = render_to_string(
        "businesses/invite_email.html",
        {
            "invite_link": invite_link,
            "business": business,
            "role": role
        }
    )

    subject = "You've been invited to join a business"

    email_message = EmailMultiAlternatives(
        subject,
        "You have been invited to join a business.",
        settings.DEFAULT_FROM_EMAIL,
        [email]
    )

    email_message.attach_alternative(html_content, "text/html")
    email_message.send(fail_silently=True)