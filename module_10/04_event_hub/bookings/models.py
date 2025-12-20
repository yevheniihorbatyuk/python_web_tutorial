from django.db import models
from django.utils import timezone
from users.models import CustomUser
from events.models import Event


class Booking(models.Model):
    """Event ticket booking/registration."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        CANCELLED = 'cancelled', 'Cancelled'
        NO_SHOW = 'no_show', 'No Show'

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='bookings')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='bookings')

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    number_of_tickets = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    registered_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    special_requirements = models.TextField(blank=True, help_text="Dietary, accessibility, etc.")

    class Meta:
        unique_together = ['event', 'user']
        ordering = ['-registered_at']
        indexes = [
            models.Index(fields=['event', 'status']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.event.title}"

    def confirm(self):
        """Confirm the booking."""
        if self.status == self.Status.PENDING:
            self.status = self.Status.CONFIRMED
            self.confirmed_at = timezone.now()
            self.save()

    def cancel(self):
        """Cancel the booking."""
        if self.status in [self.Status.PENDING, self.Status.CONFIRMED]:
            self.status = self.Status.CANCELLED
            self.cancelled_at = timezone.now()
            self.save()


class Waitlist(models.Model):
    """Waitlist for fully booked events."""

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='waitlist')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='waitlist')

    position = models.PositiveIntegerField()
    joined_at = models.DateTimeField(auto_now_add=True)
    notified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['event', 'user']
        ordering = ['position']
        indexes = [
            models.Index(fields=['event', 'position']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.event.title} (Position: {self.position})"

    @property
    def is_notified(self):
        """Check if user has been notified of available spot."""
        return self.notified_at is not None
