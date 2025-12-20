from django.db import models
from django.utils import timezone
from users.models import CustomUser
from bookings.models import Booking


class Payment(models.Model):
    """Payment transaction for event bookings."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'
        REFUNDED = 'refunded', 'Refunded'
        CANCELLED = 'cancelled', 'Cancelled'

    class Method(models.TextChoices):
        CREDIT_CARD = 'credit_card', 'Credit Card'
        DEBIT_CARD = 'debit_card', 'Debit Card'
        PAYPAL = 'paypal', 'PayPal'
        BANK_TRANSFER = 'bank_transfer', 'Bank Transfer'
        MOCK = 'mock', 'Mock Payment'

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='payments')

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    method = models.CharField(max_length=20, choices=Method.choices, default=Method.MOCK)

    transaction_id = models.CharField(max_length=100, unique=True)
    reference_number = models.CharField(max_length=50, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    refunded_at = models.DateTimeField(null=True, blank=True)

    error_message = models.TextField(blank=True, help_text="Error details if payment failed")

    metadata = models.JSONField(default=dict, blank=True, help_text="Additional payment metadata")

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status']),
            models.Index(fields=['transaction_id']),
        ]

    def __str__(self):
        return f"Payment {self.transaction_id} - {self.amount} {self.currency}"

    def complete(self):
        """Mark payment as completed."""
        if self.status == self.Status.PENDING:
            self.status = self.Status.COMPLETED
            self.processed_at = timezone.now()
            self.booking.confirm()
            self.save()

    def fail(self, error_msg=''):
        """Mark payment as failed."""
        if self.status == self.Status.PENDING:
            self.status = self.Status.FAILED
            self.processed_at = timezone.now()
            self.error_message = error_msg
            self.save()

    def refund(self):
        """Refund the payment."""
        if self.status == self.Status.COMPLETED:
            self.status = self.Status.REFUNDED
            self.refunded_at = timezone.now()
            if self.booking.status != 'cancelled':
                self.booking.cancel()
            self.save()


class Invoice(models.Model):
    """Invoice for payment transactions."""

    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='invoice')

    invoice_number = models.CharField(max_length=50, unique=True)
    issued_at = models.DateTimeField(auto_now_add=True)

    billing_address = models.TextField()
    notes = models.TextField(blank=True)

    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-issued_at']
        indexes = [
            models.Index(fields=['invoice_number']),
        ]

    def __str__(self):
        return self.invoice_number

    def mark_as_sent(self):
        """Mark invoice as sent."""
        self.is_sent = True
        self.sent_at = timezone.now()
        self.save()
