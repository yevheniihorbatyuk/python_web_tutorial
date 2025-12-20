from django.contrib import admin
from .models import Event, Session


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'organizer', 'status', 'start_date', 'attendees_count', 'max_attendees')
    list_filter = ('category', 'status', 'is_online', 'start_date')
    search_fields = ('title', 'description', 'organizer__username')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'description', 'category', 'organizer', 'tags')
        }),
        ('Location & Format', {
            'fields': ('location', 'is_online', 'online_url')
        }),
        ('Schedule', {
            'fields': ('start_date', 'end_date', 'registration_deadline')
        }),
        ('Capacity & Pricing', {
            'fields': ('max_attendees', 'price')
        }),
        ('Media', {
            'fields': ('cover_image',)
        }),
        ('Status & Timestamps', {
            'fields': ('status', 'created_at', 'updated_at')
        }),
    )


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'event', 'speaker', 'start_time', 'end_time')
    list_filter = ('event', 'start_time')
    search_fields = ('title', 'event__title', 'speaker__username')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Session Info', {
            'fields': ('event', 'title', 'description')
        }),
        ('Schedule', {
            'fields': ('start_time', 'end_time')
        }),
        ('Speaker & Location', {
            'fields': ('speaker', 'room_or_link')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
