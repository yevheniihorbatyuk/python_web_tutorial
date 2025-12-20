from celery import shared_task
from django.utils import timezone
from django.conf import settings
import random
from .models import Payment


@shared_task
def process_payment(payment_id):
    """Process mock payment transaction."""
    try:
        payment = Payment.objects.get(id=payment_id)

        # Simulate payment processing delay
        import time
        delay = int(settings.MOCK_PAYMENT_PROCESSING_DELAY)
        time.sleep(delay)

        # Mock payment success/failure logic
        success_rate = float(settings.MOCK_PAYMENT_SUCCESS_RATE)
        if random.random() < success_rate:
            payment.complete()
            # Create invoice after payment completion
            create_invoice.delay(payment.id)
        else:
            payment.fail("Mock payment failed")

        return f"Payment {payment.transaction_id} processed"

    except Payment.DoesNotExist:
        return f"Payment {payment_id} not found"


@shared_task
def create_invoice(payment_id):
    """Create invoice for completed payment."""
    try:
        from .models import Invoice
        import uuid

        payment = Payment.objects.get(id=payment_id)

        # Check if invoice already exists
        if hasattr(payment, 'invoice'):
            return f"Invoice already exists for payment {payment.transaction_id}"

        # Generate invoice number
        invoice_number = f"INV-{payment.transaction_id[-8:]}-{uuid.uuid4().hex[:4].upper()}"

        # Get billing address from user profile
        billing_address = f"{payment.user.get_full_name()}\n{payment.user.email}"
        if payment.user.organization:
            billing_address = f"{payment.user.organization}\n" + billing_address

        invoice = Invoice.objects.create(
            payment=payment,
            invoice_number=invoice_number,
            billing_address=billing_address,
            notes=f"Event: {payment.booking.event.title}"
        )

        return f"Invoice {invoice_number} created"

    except Payment.DoesNotExist:
        return f"Payment {payment_id} not found"
    except Exception as e:
        return f"Error creating invoice: {str(e)}"


@shared_task
def process_payment_timeout():
    """Process pending payments that have timed out."""
    # Find payments pending for more than 30 minutes
    from datetime import timedelta

    timeout_threshold = timezone.now() - timedelta(minutes=30)
    pending_payments = Payment.objects.filter(
        status=Payment.Status.PENDING,
        created_at__lt=timeout_threshold
    )

    count = 0
    for payment in pending_payments:
        payment.fail("Payment processing timeout")
        count += 1

    return f"Processed {count} timed out payments"
