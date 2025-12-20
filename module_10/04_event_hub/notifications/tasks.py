from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import Notification, EventCertificate
from bookings.models import Booking, Waitlist
from events.models import Event


@shared_task
def send_event_reminders():
    """Send reminders for events starting in 24 hours."""
    from datetime import timedelta

    # Find events starting in ~24 hours
    now = timezone.now()
    reminder_time = now + timedelta(hours=24)
    reminder_window = timedelta(hours=1)

    events = Event.objects.filter(
        status=Event.Status.PUBLISHED,
        start_date__gte=reminder_time - reminder_window,
        start_date__lte=reminder_time + reminder_window
    )

    count = 0
    for event in events:
        # Get confirmed attendees
        bookings = event.bookings.filter(status=Booking.Status.CONFIRMED)

        for booking in bookings:
            # Create notification
            Notification.objects.create(
                user=booking.user,
                event=event,
                notification_type=Notification.Type.EVENT_REMINDER,
                title=f"Reminder: {event.title} starts in 24 hours",
                message=f"Your registered event '{event.title}' starts at {event.start_date.strftime('%Y-%m-%d %H:%M')}. Don't forget to attend!"
            )
            count += 1

            # Send email if available
            if booking.user.email:
                send_event_reminder_email.delay(booking.user.id, event.id)

    return f"Sent {count} event reminders"


@shared_task
def send_event_reminder_email(user_id, event_id):
    """Send event reminder email."""
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()

        user = User.objects.get(id=user_id)
        event = Event.objects.get(id=event_id)

        subject = f"Reminder: {event.title} starts in 24 hours"
        message = f"""
        Hello {user.get_full_name()},

        This is a reminder that your registered event "{event.title}" starts in 24 hours.

        Event Details:
        - Title: {event.title}
        - Date: {event.start_date.strftime('%B %d, %Y at %H:%M')}
        - Location: {event.location if not event.is_online else 'Online'}

        Please make sure you have all the necessary information and materials ready.

        Best regards,
        EventHub Team
        """

        if settings.EMAIL_BACKEND != 'django.core.mail.backends.console.EmailBackend':
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=True,
            )

    except Exception as e:
        return f"Error sending email: {str(e)}"

    return "Email sent"


@shared_task
def send_post_event_surveys():
    """Send post-event survey notifications for completed events."""
    # Find events that completed in the last hour
    from datetime import timedelta

    now = timezone.now()
    survey_threshold = now - timedelta(hours=1)

    events = Event.objects.filter(
        status=Event.Status.COMPLETED,
        end_date__gte=survey_threshold,
        end_date__lte=now
    )

    count = 0
    for event in events:
        # Get attendees who haven't reviewed yet
        attendees = event.bookings.filter(status=Booking.Status.CONFIRMED)

        for booking in attendees:
            # Check if user already reviewed
            if not event.reviews.filter(user=booking.user).exists():
                # Create notification for review
                Notification.objects.create(
                    user=booking.user,
                    event=event,
                    notification_type=Notification.Type.SYSTEM_ANNOUNCEMENT,
                    title=f"Share your feedback on {event.title}",
                    message=f"We'd love to hear your thoughts about the event '{event.title}'. Please take a moment to leave a review."
                )
                count += 1

    return f"Sent {count} survey notifications"


@shared_task
def process_waitlist_notifications():
    """Process waitlist notifications when spots become available."""
    from bookings.models import Booking, Waitlist

    # Find recent cancellations
    from datetime import timedelta
    now = timezone.now()
    recent_cancellations = Booking.objects.filter(
        status=Booking.Status.CANCELLED,
        cancelled_at__gte=now - timedelta(minutes=5)
    )

    count = 0
    for booking in recent_cancellations:
        event = booking.event

        # Check if event has available spots
        if event.available_spots > 0:
            # Get first person on waitlist
            first_on_waitlist = event.waitlist.filter(notified_at__isnull=True).first()

            if first_on_waitlist:
                # Create notification
                Notification.objects.create(
                    user=first_on_waitlist.user,
                    event=event,
                    notification_type=Notification.Type.WAITLIST_AVAILABLE,
                    title=f"Spot available: {event.title}",
                    message=f"A spot has become available for the event '{event.title}' you're interested in. Book now!"
                )

                # Mark as notified
                first_on_waitlist.notified_at = now
                first_on_waitlist.save()
                count += 1

    return f"Notified {count} users from waitlist"


@shared_task
def issue_event_certificates(event_id):
    """Issue certificates to event attendees."""
    import uuid

    try:
        event = Event.objects.get(id=event_id)

        # Get confirmed attendees
        bookings = event.bookings.filter(status=Booking.Status.CONFIRMED)

        count = 0
        for booking in bookings:
            # Check if certificate already exists
            if not event.certificates.filter(user=booking.user).exists():
                # Calculate hours completed
                hours_completed = (event.end_date - event.start_date).total_seconds() / 3600

                # Generate certificate number
                cert_number = f"CERT-{event.id}-{booking.user.id}-{uuid.uuid4().hex[:6].upper()}"

                # Create certificate
                cert = EventCertificate.objects.create(
                    event=event,
                    user=booking.user,
                    certificate_number=cert_number,
                    hours_completed=hours_completed,
                    skill_tags=event.tags
                )

                # Create notification
                Notification.objects.create(
                    user=booking.user,
                    event=event,
                    notification_type=Notification.Type.SYSTEM_ANNOUNCEMENT,
                    title=f"Certificate issued for {event.title}",
                    message=f"Congratulations! Your certificate for '{event.title}' is ready to download."
                )

                count += 1

        return f"Issued {count} certificates"

    except Event.DoesNotExist:
        return f"Event {event_id} not found"
