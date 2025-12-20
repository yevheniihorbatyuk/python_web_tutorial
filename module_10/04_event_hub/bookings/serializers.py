from rest_framework import serializers
from .models import Booking, Waitlist
from events.models import Event


class BookingSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    event_title = serializers.CharField(source='event.title', read_only=True)

    class Meta:
        model = Booking
        fields = (
            'id', 'event', 'event_title', 'user', 'user_name',
            'status', 'number_of_tickets', 'total_price',
            'special_requirements', 'registered_at', 'confirmed_at', 'cancelled_at'
        )
        read_only_fields = ('user', 'registered_at', 'confirmed_at', 'cancelled_at')


class BookingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating bookings."""

    class Meta:
        model = Booking
        fields = ('event', 'number_of_tickets', 'special_requirements')

    def validate(self, data):
        event = data['event']
        number_of_tickets = data.get('number_of_tickets', 1)

        # Check if event is registration open
        if not event.is_registration_open:
            raise serializers.ValidationError("Registration is closed for this event.")

        # Check availability
        if number_of_tickets > event.available_spots:
            raise serializers.ValidationError(
                f"Only {event.available_spots} spots available for this event."
            )

        return data

    def create(self, validated_data):
        user = self.context['request'].user
        event = validated_data['event']
        number_of_tickets = validated_data.get('number_of_tickets', 1)

        # Check if user already booked
        if Booking.objects.filter(event=event, user=user).exists():
            raise serializers.ValidationError("You have already booked this event.")

        total_price = event.price * number_of_tickets

        booking = Booking.objects.create(
            event=event,
            user=user,
            number_of_tickets=number_of_tickets,
            total_price=total_price,
            special_requirements=validated_data.get('special_requirements', '')
        )

        return booking


class WaitlistSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    event_title = serializers.CharField(source='event.title', read_only=True)

    class Meta:
        model = Waitlist
        fields = (
            'id', 'event', 'event_title', 'user', 'user_name',
            'position', 'joined_at', 'notified_at', 'is_notified'
        )
        read_only_fields = ('position', 'joined_at', 'notified_at')


class WaitlistCreateSerializer(serializers.ModelSerializer):
    """Serializer for joining waitlist."""

    class Meta:
        model = Waitlist
        fields = ('event',)

    def validate(self, data):
        event = data['event']
        user = self.context['request'].user

        # Check if user already on waitlist
        if Waitlist.objects.filter(event=event, user=user).exists():
            raise serializers.ValidationError("You are already on the waitlist for this event.")

        # Check if user already booked
        if Booking.objects.filter(event=event, user=user).exists():
            raise serializers.ValidationError("You have already booked this event.")

        return data

    def create(self, validated_data):
        event = validated_data['event']
        user = self.context['request'].user

        # Get next position
        last_position = Waitlist.objects.filter(event=event).order_by('-position').first()
        position = (last_position.position if last_position else 0) + 1

        waitlist = Waitlist.objects.create(
            event=event,
            user=user,
            position=position
        )

        return waitlist
