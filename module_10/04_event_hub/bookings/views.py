from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from .models import Booking, Waitlist
from .serializers import (
    BookingSerializer, BookingCreateSerializer,
    WaitlistSerializer, WaitlistCreateSerializer
)


class BookingViewSet(viewsets.ModelViewSet):
    """ViewSet for Booking model."""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['event', 'status']
    ordering_fields = ['registered_at']
    ordering = ['-registered_at']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Booking.objects.all()
        return Booking.objects.filter(user=user)

    def get_serializer_class(self):
        if self.action == 'create':
            return BookingCreateSerializer
        return BookingSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirm a pending booking."""
        booking = self.get_object()
        if booking.status != Booking.Status.PENDING:
            return Response(
                {'error': 'Only pending bookings can be confirmed.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        booking.confirm()
        return Response(BookingSerializer(booking).data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a booking."""
        booking = self.get_object()
        booking.cancel()
        return Response(BookingSerializer(booking).data)


class WaitlistViewSet(viewsets.ModelViewSet):
    """ViewSet for Waitlist model."""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['event']
    ordering_fields = ['position']
    ordering = ['position']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Waitlist.objects.all()
        return Waitlist.objects.filter(user=user)

    def get_serializer_class(self):
        if self.action == 'create':
            return WaitlistCreateSerializer
        return WaitlistSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """Leave the waitlist."""
        waitlist = self.get_object()
        waitlist.delete()
        return Response({'status': 'left waitlist'}, status=status.HTTP_204_NO_CONTENT)
