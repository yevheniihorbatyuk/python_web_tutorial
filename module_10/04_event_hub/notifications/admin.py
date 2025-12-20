from django.contrib import admin
from .models import Notification, EventReview, EventCertificate


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'user__username')
    readonly_fields = ('created_at', 'read_at')
    actions = ['mark_as_read']

    fieldsets = (
        ('Notification Info', {
            'fields': ('user', 'event', 'notification_type', 'title')
        }),
        ('Content', {
            'fields': ('message',)
        }),
        ('Status', {
            'fields': ('is_read', 'created_at', 'read_at')
        }),
    )

    def mark_as_read(self, request, queryset):
        for notification in queryset:
            notification.mark_as_read()
        self.message_user(request, f"{queryset.count()} notifications marked as read.")

    mark_as_read.short_description = "Mark selected notifications as read"


@admin.register(EventReview)
class EventReviewAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'rating', 'attended', 'helpful_percentage', 'created_at')
    list_filter = ('rating', 'attended', 'created_at', 'event')
    search_fields = ('event__title', 'user__username', 'title', 'review')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Review Info', {
            'fields': ('event', 'user', 'rating', 'attended')
        }),
        ('Review Content', {
            'fields': ('title', 'review')
        }),
        ('Feedback Stats', {
            'fields': ('helpful_count', 'unhelpful_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(EventCertificate)
class EventCertificateAdmin(admin.ModelAdmin):
    list_display = ('certificate_number', 'user', 'event', 'hours_completed', 'is_downloaded', 'issued_date')
    list_filter = ('is_downloaded', 'issued_date', 'event')
    search_fields = ('certificate_number', 'user__username', 'event__title')
    readonly_fields = ('certificate_number', 'issued_date', 'downloaded_at')
    actions = ['mark_as_downloaded']

    fieldsets = (
        ('Certificate Info', {
            'fields': ('certificate_number', 'event', 'user')
        }),
        ('Completion Details', {
            'fields': ('hours_completed', 'skill_tags')
        }),
        ('Files & Downloads', {
            'fields': ('pdf_file', 'is_downloaded', 'issued_date', 'downloaded_at')
        }),
    )

    def mark_as_downloaded(self, request, queryset):
        for cert in queryset:
            cert.mark_as_downloaded()
        self.message_user(request, f"{queryset.count()} certificates marked as downloaded.")

    mark_as_downloaded.short_description = "Mark selected certificates as downloaded"
