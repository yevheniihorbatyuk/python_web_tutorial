"""
User models for Event Hub.

Includes custom user model with roles and profile information.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class CustomUser(AbstractUser):
    """Custom user model with additional fields for Event Hub."""

    class UserType(models.TextChoices):
        ATTENDEE = 'attendee', 'Attendee'
        ORGANIZER = 'organizer', 'Organizer'
        ADMIN = 'admin', 'Admin'

    # Extend Django's user model
    user_type = models.CharField(
        max_length=20,
        choices=UserType.choices,
        default=UserType.ATTENDEE,
        help_text="Role in the system"
    )

    # Additional profile fields
    bio = models.TextField(
        blank=True,
        help_text="User biography"
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Phone number"
    )

    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        help_text="Profile picture"
    )

    website = models.URLField(
        blank=True,
        help_text="Personal website"
    )

    organization = models.CharField(
        max_length=200,
        blank=True,
        help_text="Company or organization name"
    )

    # Metadata
    is_verified = models.BooleanField(
        default=False,
        help_text="Email verified"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['user_type']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.get_full_name() or self.username}"

    def get_full_name(self):
        """Return user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name or self.username

    def is_organizer(self):
        """Check if user is an organizer."""
        return self.user_type == self.UserType.ORGANIZER

    def is_event_admin(self):
        """Check if user is an admin."""
        return self.user_type == self.UserType.ADMIN


class UserProfile(models.Model):
    """Extended user profile with social links and preferences."""

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='profile',
        primary_key=True
    )

    # Social links
    twitter = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    github = models.URLField(blank=True)
    facebook = models.URLField(blank=True)

    # Preferences
    newsletter_subscribed = models.BooleanField(
        default=True,
        help_text="Subscribed to newsletter"
    )

    notifications_enabled = models.BooleanField(
        default=True,
        help_text="Email notifications enabled"
    )

    # Statistics
    total_events_attended = models.IntegerField(default=0)
    total_events_organized = models.IntegerField(default=0)
    total_spent = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Total amount spent on events"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self):
        return f"Profile of {self.user.get_full_name()}"
