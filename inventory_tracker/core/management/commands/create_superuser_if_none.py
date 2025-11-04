from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from decouple import config

class Command(BaseCommand):
    help = "Create a superuser if none exists"

    def handle(self, *args, **kwargs):
        User = get_user_model()

        if not User.objects.filter(is_superuser=True).exists():
            email = config("DJANGO_SUPERUSER_EMAIL", default="admin@example.com")
            password = config("DJANGO_SUPERUSER_PASSWORD", default="admin123")
            first_name = config("DJANGO_SUPERUSER_FIRSTNAME", default="Admin")
            last_name = config("DJANGO_SUPERUSER_LASTNAME", default="User")

            User.objects.create_superuser(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role='admin',
                is_active=True
            )
            self.stdout.write(self.style.SUCCESS("✅ Superuser created successfully"))
        else:
            self.stdout.write("Superuser already exists.")
