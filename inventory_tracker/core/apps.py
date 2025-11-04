from django.apps import AppConfig
from django.contrib.auth import get_user_model
from decouple import config

class CoreConfig(AppConfig):  # change to your app name (e.g., core)
    name = 'core'  # must match the app folder name

    def ready(self):
        User = get_user_model()

        # Read from environment variables
        email = config("DJANGO_SUPERUSER_EMAIL", default="admin@example.com")
        password = config("DJANGO_SUPERUSER_PASSWORD", default="admin123")
        first_name = config("DJANGO_SUPERUSER_FIRSTNAME", default="Admin")
        last_name = config("DJANGO_SUPERUSER_LASTNAME", default="User")

        # Only create if it doesn’t exist
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role='admin',
                is_active=True
            )
            print("✅ Superuser created successfully!")
