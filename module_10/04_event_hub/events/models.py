from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from users.models import CustomUser


class Event(models.Model):
    """Main event model for master classes and community events."""

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PUBLISHED = 'published', 'Published'
        ONGOING = 'ongoing', 'Ongoing'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'

    class Category(models.TextChoices):
        WORKSHOP = 'workshop', 'Workshop'
        WEBINAR = 'webinar', 'Webinar'
        CONFERENCE = 'conference', 'Conference'
        MASTERCLASS = 'masterclass', 'Master Class'
        MEETUP = 'meetup', 'Meetup'
        TRAINING = 'training', 'Training'

    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=Category.choices)
    organizer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='organized_events')

    location = models.CharField(max_length=300)
    is_online = models.BooleanField(default=False)
    online_url = models.URLField(blank=True, help_text="Zoom/Meet link for online events")

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    registration_deadline = models.DateTimeField()

    max_attendees = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    cover_image = models.ImageField(upload_to='event_covers/', blank=True, null=True)

    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['status', 'start_date']),
            models.Index(fields=['organizer']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return self.title

    @property
    def is_registration_open(self):
        """Check if registration is still open."""
        return timezone.now() < self.registration_deadline

    @property
    def attendees_count(self):
        """Get current number of confirmed attendees."""
        return self.bookings.filter(status='confirmed').count()

    @property
    def available_spots(self):
        """Get number of available spots."""
        return max(0, self.max_attendees - self.attendees_count)


class Session(models.Model):
    """Individual sessions within an event (for multi-day events)."""

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='sessions')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    speaker = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sessions_speaking'
    )

    room_or_link = models.CharField(max_length=300, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['start_time']
        indexes = [
            models.Index(fields=['event', 'start_time']),
        ]

    def __str__(self):
        return f"{self.event.title} - {self.title}"
