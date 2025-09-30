from django.db import migrations
from django.contrib.auth import get_user_model
from decouple import config  # <- import config

def create_superuser(apps, schema_editor):
    User = get_user_model()

    # Use config() to read from .env
    email = config("DJANGO_SUPERUSER_EMAIL", default="admin@example.com")
    password = config("DJANGO_SUPERUSER_PASSWORD", default="StrongPassword123")
    first_name = config("DJANGO_SUPERUSER_FIRSTNAME", default="Admin")
    last_name = config("DJANGO_SUPERUSER_LASTNAME", default="User")

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
    email = config("DJANGO_SUPERUSER_EMAIL", default=None)
    if email:
        User.objects.filter(email=email).delete()
        print(f"🗑️ Superuser with email {email} deleted.")

class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_superuser, remove_superuser),
    ]
