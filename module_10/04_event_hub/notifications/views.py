from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Notification, EventReview, EventCertificate
from .serializers import (
    NotificationSerializer, NotificationUpdateSerializer,
    EventReviewSerializer, EventReviewCreateSerializer,
    EventCertificateSerializer, EventCertificateDownloadSerializer
)


class NotificationViewSet(viewsets.ModelViewSet):
    """ViewSet for Notification model."""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['notification_type', 'is_read', 'event']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'partial_update' or self.action == 'update':
            return NotificationUpdateSerializer
        return NotificationSerializer

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Mark notification as read."""
        notification = self.get_object()
        notification.mark_as_read()
        return Response(NotificationSerializer(notification).data)

    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """Mark all notifications as read."""
        notifications = self.get_queryset().filter(is_read=False)
        for notification in notifications:
            notification.mark_as_read()
        return Response({'marked': notifications.count()})

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread notifications."""
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'unread_count': count})


class EventReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for EventReview model."""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['event', 'rating']
    search_fields = ['event__title', 'title']
    ordering_fields = ['rating', 'created_at', 'helpful_count']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return EventReviewCreateSerializer
        return EventReviewSerializer

    def get_queryset(self):
        return EventReview.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_helpful(self, request, pk=None):
        """Mark review as helpful."""
        review = self.get_object()
        review.helpful_count += 1
        review.save()
        return Response(EventReviewSerializer(review).data)

    @action(detail=True, methods=['post'])
    def mark_unhelpful(self, request, pk=None):
        """Mark review as unhelpful."""
        review = self.get_object()
        review.unhelpful_count += 1
        review.save()
        return Response(EventReviewSerializer(review).data)


class EventCertificateViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for EventCertificate model."""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['event', 'is_downloaded']
    search_fields = ['certificate_number', 'event__title']
    ordering_fields = ['issued_date']
    ordering = ['-issued_date']

    serializer_class = EventCertificateSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return EventCertificate.objects.all()
        return EventCertificate.objects.filter(user=user)

    @action(detail=True, methods=['post'])
    def mark_as_downloaded(self, request, pk=None):
        """Mark certificate as downloaded."""
        certificate = self.get_object()
        certificate.mark_as_downloaded()
        return Response(EventCertificateSerializer(certificate).data)
