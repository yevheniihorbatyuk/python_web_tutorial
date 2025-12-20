from django.db import models
from django.utils import timezone
from users.models import CustomUser
from events.models import Event


class Notification(models.Model):
    """User notifications for events and system updates."""

    class Type(models.TextChoices):
        EVENT_REMINDER = 'event_reminder', 'Event Reminder'
        BOOKING_CONFIRMATION = 'booking_confirmation', 'Booking Confirmation'
        PAYMENT_RECEIVED = 'payment_received', 'Payment Received'
        EVENT_CANCELLED = 'event_cancelled', 'Event Cancelled'
        EVENT_UPDATED = 'event_updated', 'Event Updated'
        WAITLIST_AVAILABLE = 'waitlist_available', 'Waitlist Spot Available'
        SYSTEM_ANNOUNCEMENT = 'system_announcement', 'System Announcement'

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')

    notification_type = models.CharField(max_length=25, choices=Type.choices)
    title = models.CharField(max_length=200)
    message = models.TextField()

    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['notification_type']),
        ]

    def __str__(self):
        return f"{self.title} - {self.user.username}"

    def mark_as_read(self):
        """Mark notification as read."""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()


class EventReview(models.Model):
    """Reviews and ratings for events."""

    class Rating(models.IntegerChoices):
        POOR = 1, 'Poor'
        FAIR = 2, 'Fair'
        GOOD = 3, 'Good'
        VERY_GOOD = 4, 'Very Good'
        EXCELLENT = 5, 'Excellent'

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='event_reviews')

    rating = models.IntegerField(choices=Rating.choices)
    title = models.CharField(max_length=200)
    review = models.TextField()

    attended = models.BooleanField(default=True, help_text="Did the user attend the event?")

    helpful_count = models.PositiveIntegerField(default=0)
    unhelpful_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['event', 'user']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['event', 'rating']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"{self.event.title} - {self.rating} stars by {self.user.username}"

    @property
    def helpful_percentage(self):
        """Calculate helpful percentage."""
        total = self.helpful_count + self.unhelpful_count
        if total == 0:
            return 0
        return (self.helpful_count / total) * 100


class EventCertificate(models.Model):
    """Certificates issued to attendees for completing events."""

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='certificates')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='certificates')

    certificate_number = models.CharField(max_length=50, unique=True)
    issued_date = models.DateTimeField(auto_now_add=True)

    hours_completed = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    skill_tags = models.CharField(max_length=500, blank=True, help_text="Skills acquired")

    pdf_file = models.FileField(upload_to='certificates/', null=True, blank=True)
    is_downloaded = models.BooleanField(default=False)
    downloaded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['event', 'user']
        ordering = ['-issued_date']
        indexes = [
            models.Index(fields=['certificate_number']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"Certificate {self.certificate_number} - {self.user.username}"

    def mark_as_downloaded(self):
        """Mark certificate as downloaded."""
        self.is_downloaded = True
        self.downloaded_at = timezone.now()
        self.save()
