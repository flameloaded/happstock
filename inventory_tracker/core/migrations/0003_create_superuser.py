from django.db import migrations
from django.contrib.auth import get_user_model
import os

def create_superuser(apps, schema_editor):
    User = get_user_model()

    email = os.environ["DJANGO_SUPERUSER_EMAIL"]
    password = os.environ["DJANGO_SUPERUSER_PASSWORD"]
    first_name = os.environ.get("DJANGO_SUPERUSER_FIRSTNAME", "Admin")
    last_name = os.environ.get("DJANGO_SUPERUSER_LASTNAME", "User")

    if not User.objects.filter(email=email).exists():
        User.objects.create_superuser(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        print(f"✅ Superuser created with email: {email}")
    else:
        print(f"⚠️ Superuser with email {email} already exists.")

def remove_superuser(apps, schema_editor):
    User = get_user_model()
    email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
    if email:
        User.objects.filter(email=email).delete()
        print(f"🗑️ Superuser with email {email} deleted.")

class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),  # change to your last migration
    ]

    operations = [
        migrations.RunPython(create_superuser, remove_superuser),
    ]
