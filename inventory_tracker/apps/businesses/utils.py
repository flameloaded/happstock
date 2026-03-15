from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

import requests
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

    url = "https://api.brevo.com/v3/smtp/email"

    headers = {
        "accept": "application/json",
        "api-key": settings.EMAIL_HOST_PASSWORD,
        "content-type": "application/json"
    }

    payload = {
        "sender": {
            "email": settings.DEFAULT_FROM_EMAIL
        },
        "to": [
            {"email": email}
        ],
        "subject": subject,
        "htmlContent": html_content
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 201:
        print("Email sending failed:", response.text)

    return response.json()