from rest_framework import serializers
from .models import Notification, EventReview, EventCertificate


class NotificationSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    event_title = serializers.CharField(source='event.title', read_only=True)

    class Meta:
        model = Notification
        fields = (
            'id', 'user', 'user_name', 'event', 'event_title',
            'notification_type', 'title', 'message',
            'is_read', 'created_at', 'read_at'
        )
        read_only_fields = ('created_at', 'read_at')


class NotificationUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating notification read status."""

    class Meta:
        model = Notification
        fields = ('is_read',)


class EventReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    event_title = serializers.CharField(source='event.title', read_only=True)
    helpful_percentage = serializers.FloatField(read_only=True)

    class Meta:
        model = EventReview
        fields = (
            'id', 'event', 'event_title', 'user', 'user_name',
            'rating', 'title', 'review', 'attended',
            'helpful_count', 'unhelpful_count', 'helpful_percentage',
            'created_at', 'updated_at'
        )
        read_only_fields = ('helpful_count', 'unhelpful_count', 'created_at', 'updated_at')


class EventReviewCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating event reviews."""

    class Meta:
        model = EventReview
        fields = ('event', 'rating', 'title', 'review', 'attended')

    def validate_rating(self, value):
        if value not in [1, 2, 3, 4, 5]:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        event = validated_data['event']

        # Check if review already exists
        if EventReview.objects.filter(event=event, user=user).exists():
            raise serializers.ValidationError("You have already reviewed this event.")

        review = EventReview.objects.create(
            user=user,
            **validated_data
        )

        return review


class EventCertificateSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    event_title = serializers.CharField(source='event.title', read_only=True)

    class Meta:
        model = EventCertificate
        fields = (
            'id', 'event', 'event_title', 'user', 'user_name',
            'certificate_number', 'hours_completed', 'skill_tags',
            'pdf_file', 'is_downloaded', 'issued_date', 'downloaded_at'
        )
        read_only_fields = ('certificate_number', 'issued_date', 'downloaded_at', 'pdf_file')


class EventCertificateDownloadSerializer(serializers.ModelSerializer):
    """Serializer for downloading certificates."""

    class Meta:
        model = EventCertificate
        fields = ('is_downloaded',)
