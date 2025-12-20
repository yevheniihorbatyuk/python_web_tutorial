"""
Django admin configuration for users app.
"""

from django.contrib import admin
from .models import Country, City, User


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    """Admin for Country model."""

    list_display = ('name', 'code', 'population', 'city_count', 'user_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'code')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('name',)

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code')
        }),
        ('Statistics', {
            'fields': ('population',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    """Admin for City model."""

    list_display = ('name', 'country', 'population', 'founded_year', 'is_capital', 'user_count', 'created_at')
    list_filter = ('country', 'is_capital', 'created_at')
    search_fields = ('name', 'country__name')
    readonly_fields = ('created_at', 'updated_at', 'user_count')
    ordering = ('country', 'name')

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'country', 'is_capital')
        }),
        ('Statistics', {
            'fields': ('population', 'founded_year', 'user_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def user_count(self, obj):
        """Display number of users in city."""
        return obj.user_count()
    user_count.short_description = 'Users'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Admin for User model."""

    list_display = ('full_name', 'email', 'city', 'phone', 'is_active', 'created_at')
    list_filter = ('is_active', 'city__country', 'city', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'city__name')
    readonly_fields = ('created_at', 'updated_at', 'get_location_display')
    ordering = ('-created_at',)

    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Location', {
            'fields': ('city', 'get_location_display')
        }),
        ('Bio & Status', {
            'fields': ('bio', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def full_name(self, obj):
        """Display full name."""
        return obj.full_name()
    full_name.short_description = 'Name'

    def get_location_display(self, obj):
        """Display full location."""
        return obj.get_location_string() or 'Not specified'
    get_location_display.short_description = 'Location'

    def save_model(self, request, obj, form, change):
        """Override save to add custom logic if needed."""
        super().save_model(request, obj, form, change)
