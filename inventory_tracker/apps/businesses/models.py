
# Create your models here.
"""
Handles:
    Businesses
    Staff
    Branches
    Invitations
"""

from django.db import models
from apps.core.models import User
import uuid
from django.db import models
from django.utils import timezone
from datetime import timedelta




    


class Business(models.Model):

    name = models.CharField(max_length=255)

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="owned_businesses"
    )
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    





    


class Branch(models.Model):

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="branches"
    )

    name = models.CharField(max_length=255)

    location = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f"{self.name} - {self.business.name}"
    
class BusinessMembership(models.Model):

    ROLE_CHOICES = [
        ("owner", "Owner"),
        ("manager", "Manager"),
        ("attendant", "Attendant"),
    ]

    user = models.ForeignKey("core.User", on_delete=models.CASCADE)
    business = models.ForeignKey("Business", on_delete=models.CASCADE)
    branch = models.ForeignKey(
        Branch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    # Permissions
    can_create_product = models.BooleanField(default=False)
    can_delete_product = models.BooleanField(default=False)
    can_view_sales = models.BooleanField(default=False)
    can_manage_staff = models.BooleanField(default=False)
    can_sell = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.business.name}"


class BusinessInvitation(models.Model):

    ROLE_CHOICES = [
        ("manager", "Manager"),
        ("attendant", "Attendant"),
    ]
    branch = models.ForeignKey(
        "Branch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    business = models.ForeignKey("Business", on_delete=models.CASCADE)

    email = models.EmailField()

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    token = models.UUIDField(default=uuid.uuid4, unique=True)

    invited_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_business_invites"
    )

    last_sent_at = models.DateTimeField(null=True, blank=True)
    
    accepted = models.BooleanField(default=False)

    # NEW FIELD
    expires_at = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Automatically set expiration if not already set
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=1)
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"{self.email} invited to {self.business.name}"