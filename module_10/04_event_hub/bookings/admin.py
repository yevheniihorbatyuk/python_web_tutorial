from django.contrib import admin
from .models import Booking, Waitlist


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'status', 'number_of_tickets', 'total_price', 'registered_at')
    list_filter = ('status', 'registered_at', 'event')
    search_fields = ('user__username', 'event__title')
    readonly_fields = ('registered_at', 'confirmed_at', 'cancelled_at')
    actions = ['confirm_bookings', 'cancel_bookings']

    fieldsets = (
        ('Booking Info', {
            'fields': ('event', 'user', 'status')
        }),
        ('Tickets & Price', {
            'fields': ('number_of_tickets', 'total_price')
        }),
        ('Special Requirements', {
            'fields': ('special_requirements',)
        }),
        ('Timestamps', {
            'fields': ('registered_at', 'confirmed_at', 'cancelled_at')
        }),
    )

    def confirm_bookings(self, request, queryset):
        for booking in queryset:
            booking.confirm()
        self.message_user(request, f"{queryset.count()} bookings confirmed.")

    def cancel_bookings(self, request, queryset):
        for booking in queryset:
            booking.cancel()
        self.message_user(request, f"{queryset.count()} bookings cancelled.")

    confirm_bookings.short_description = "Confirm selected bookings"
    cancel_bookings.short_description = "Cancel selected bookings"


@admin.register(Waitlist)
class WaitlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'position', 'joined_at', 'is_notified')
    list_filter = ('event', 'joined_at')
    search_fields = ('user__username', 'event__title')
    readonly_fields = ('position', 'joined_at', 'notified_at')
    fieldsets = (
        ('Waitlist Entry', {
            'fields': ('event', 'user', 'position')
        }),
        ('Timestamps', {
            'fields': ('joined_at', 'notified_at')
        }),
    )
