from rest_framework import serializers
from .models import Event, Session


class SessionSerializer(serializers.ModelSerializer):
    speaker_name = serializers.CharField(source='speaker.get_full_name', read_only=True)

    class Meta:
        model = Session
        fields = ('id', 'title', 'description', 'start_time', 'end_time', 'speaker', 'speaker_name', 'room_or_link', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')


class EventSerializer(serializers.ModelSerializer):
    organizer_name = serializers.CharField(source='organizer.get_full_name', read_only=True)
    sessions = SessionSerializer(many=True, read_only=True)
    attendees_count = serializers.IntegerField(read_only=True)
    available_spots = serializers.IntegerField(read_only=True)
    is_registration_open = serializers.BooleanField(read_only=True)

    class Meta:
        model = Event
        fields = (
            'id', 'title', 'description', 'category', 'organizer', 'organizer_name',
            'location', 'is_online', 'online_url', 'status',
            'start_date', 'end_date', 'registration_deadline',
            'max_attendees', 'attendees_count', 'available_spots', 'is_registration_open',
            'price', 'cover_image', 'tags', 'sessions',
            'created_at', 'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at')


class EventListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing events."""
    organizer_name = serializers.CharField(source='organizer.get_full_name', read_only=True)
    attendees_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Event
        fields = (
            'id', 'title', 'category', 'organizer_name',
            'location', 'is_online', 'status',
            'start_date', 'end_date',
            'max_attendees', 'attendees_count', 'price', 'cover_image'
        )


class EventCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating events (organizers only)."""

    class Meta:
        model = Event
        fields = (
            'title', 'description', 'category',
            'location', 'is_online', 'online_url',
            'start_date', 'end_date', 'registration_deadline',
            'max_attendees', 'price', 'cover_image', 'tags'
        )

    def validate(self, data):
        if data['start_date'] >= data['end_date']:
            raise serializers.ValidationError("Start date must be before end date.")
        if data['registration_deadline'] >= data['start_date']:
            raise serializers.ValidationError("Registration deadline must be before start date.")
        return data
