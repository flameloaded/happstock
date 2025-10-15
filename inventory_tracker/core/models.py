from django.contrib.auth.models import BaseUserManager,AbstractBaseUser,PermissionsMixin
from django.db import models
from django.utils import timezone
from datetime import timedelta
import random







REGISTRATION_CHOICES = [
    ('email', 'Email'),
    ('google', 'Google')
]

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models


REGISTRATION_CHOICES = (
    ('email', 'Email'),
    ('google', 'Google'),
)




class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('staff', 'Staff'),
        ('user', 'User'),
    )

    REGISTRATION_CHOICES = (
        ('email', 'Email'),
        ('google', 'Google'),
    )

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    registration_method = models.CharField(max_length=20, choices=REGISTRATION_CHOICES, default='email')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')

    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    # 🔹 Verification fields
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    code_expires_at = models.DateTimeField(blank=True, null=True)

    USERNAME_FIELD = 'email'
    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name or ''} {self.last_name or ''}".strip()

    # ✅ Generate verification code
    def generate_verification_code(self):
        # If the code exists and hasn’t expired yet
        if self.code_expires_at and timezone.now() < self.code_expires_at:
            raise ValueError("A verification code has already been sent. Please wait until it expires.")

        # Otherwise, generate a new one
        code = str(random.randint(100000, 999999))
        self.verification_code = code
        self.code_expires_at = timezone.now() + timedelta(minutes=10)
        self.save(update_fields=['verification_code', 'code_expires_at'])
        return code

    def verify_code(self, code):
        if (
            self.verification_code == code and
            self.code_expires_at and
            timezone.now() < self.code_expires_at
        ):
            return True
        return False

    def resend_verification_code(self):
        if self.code_expires_at and timezone.now() < self.code_expires_at:
            raise ValueError("You can only request a new code after the current one expires.")
        return self.generate_verification_code()
