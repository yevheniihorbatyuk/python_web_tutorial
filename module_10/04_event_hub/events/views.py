from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import Event, Session
from .serializers import (
    EventSerializer, EventListSerializer, EventCreateUpdateSerializer,
    SessionSerializer
)


class EventViewSet(viewsets.ModelViewSet):
    """ViewSet for Event model."""
    queryset = Event.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'status', 'is_online']
    search_fields = ['title', 'description', 'tags']
    ordering_fields = ['start_date', 'created_at', 'price']
    ordering = ['-start_date']

    def get_serializer_class(self):
        if self.action == 'list':
            return EventListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return EventCreateUpdateSerializer
        return EventSerializer

    def get_permissions(self):
        if self.action in ['create']:
            permission_classes = [IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)

    @action(detail=True, methods=['get'])
    def attendees(self, request, pk=None):
        """Get list of confirmed attendees for an event."""
        event = self.get_object()
        bookings = event.bookings.filter(status='confirmed')
        from bookings.serializers import BookingSerializer
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Publish a draft event."""
        event = self.get_object()
        if event.status != Event.Status.DRAFT:
            return Response(
                {'error': 'Only draft events can be published.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        event.status = Event.Status.PUBLISHED
        event.save()
        return Response(EventSerializer(event).data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an event."""
        event = self.get_object()
        if event.status in [Event.Status.COMPLETED, Event.Status.CANCELLED]:
            return Response(
                {'error': f'Cannot cancel {event.status} event.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        event.status = Event.Status.CANCELLED
        event.save()
        return Response(EventSerializer(event).data)

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get event statistics."""
        event = self.get_object()
        return Response({
            'total_attendees': event.attendees_count,
            'available_spots': event.available_spots,
            'waitlist_count': event.waitlist.count(),
            'reviews_count': event.reviews.count(),
            'average_rating': self._get_average_rating(event),
            'total_revenue': self._get_total_revenue(event)
        })

    def _get_average_rating(self, event):
        reviews = event.reviews.all()
        if not reviews.exists():
            return 0
        return sum(r.rating for r in reviews) / reviews.count()

    def _get_total_revenue(self, event):
        from payments.models import Payment
        payments = Payment.objects.filter(
            booking__event=event,
            status=Payment.Status.COMPLETED
        )
        total = sum(p.amount for p in payments)
        return float(total)


class SessionViewSet(viewsets.ModelViewSet):
    """ViewSet for Session model."""
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['event', 'speaker']
    ordering_fields = ['start_time']
    ordering = ['start_time']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]
