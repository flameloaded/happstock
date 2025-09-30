from django.apps import AppConfig
import os

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()

        email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

        if email and password:
            if not User.objects.filter(email=email).exists():
                User.objects.create_superuser(
                    email=email,
                    password=password,
                    first_name="Admin",
                    last_name="User"
                )
                print(f"✅ Superuser created with email: {email}")
