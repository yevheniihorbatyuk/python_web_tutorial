from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = (
            'twitter', 'linkedin', 'github', 'facebook',
            'newsletter_subscribed', 'notifications_enabled',
            'total_events_attended', 'total_events_organized', 'total_spent',
            'created_at', 'updated_at'
        )
        read_only_fields = ('total_events_attended', 'total_events_organized', 'total_spent', 'created_at', 'updated_at')


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    is_organizer = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'user_type', 'bio', 'phone', 'avatar', 'website', 'organization',
            'is_verified', 'is_active', 'is_organizer', 'profile',
            'date_joined', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'date_joined', 'created_at', 'updated_at')


class UserListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing users."""
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'full_name', 'user_type', 'avatar', 'organization')


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm', 'first_name', 'last_name', 'user_type')

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password': 'Passwords do not match.'})

        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({'email': 'Email already registered.'})

        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')

        user = User.objects.create_user(
            **validated_data,
            password=password,
            is_active=True
        )

        # Create profile
        UserProfile.objects.create(user=user)

        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile."""

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'email',
            'bio', 'phone', 'avatar', 'website', 'organization'
        )

    def validate_email(self, value):
        user = self.context['request'].user
        if User.objects.filter(email=value).exclude(id=user.id).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile settings."""

    class Meta:
        model = UserProfile
        fields = (
            'twitter', 'linkedin', 'github', 'facebook',
            'newsletter_subscribed', 'notifications_enabled'
        )


class UserDetailSerializer(serializers.ModelSerializer):
    """Detailed user serializer including profile and statistics."""
    profile = UserProfileSerializer(read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    is_organizer = serializers.BooleanField(read_only=True)
    events_organized_count = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'user_type', 'bio', 'phone', 'avatar', 'website', 'organization',
            'is_verified', 'is_active', 'is_organizer', 'profile',
            'events_organized_count', 'reviews_count',
            'date_joined', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'date_joined', 'created_at', 'updated_at')

    def get_events_organized_count(self, obj):
        return obj.organized_events.filter(status='published').count()

    def get_reviews_count(self, obj):
        return obj.event_reviews.count()
