from django.contrib import admin

from apps.core.admin import ReadOnlyAdminMixin

from .models import Notification

# =============================================================================
# Notifications (created and sent by the system, so view-only)
# =============================================================================


@admin.register(Notification)
class NotificationAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = (
        "created_at",
        "recipient",
        "notification_type",
        "title",
        "channel",
        "status",
        "read_at",
    )
    list_filter = ("notification_type", "channel", "status")
    search_fields = ("title", "recipient__full_name", "recipient__phone_number")
    list_select_related = ("recipient",)
    date_hierarchy = "created_at"
    fieldsets = (
        ("Notification", {"fields": ("id", "recipient", "notification_type", "title", "message")}),
        ("Source", {"fields": ("trip_event", "geofence_event", "sos_alert")}),
        ("Delivery", {"fields": ("channel", "status", "sent_at", "read_at")}),
        ("Dates", {"fields": ("created_at", "updated_at")}),
    )
