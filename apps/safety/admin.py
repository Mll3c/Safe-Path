from django.contrib import admin

from apps.core.admin import ReadOnlyAdminMixin

from .models import EmergencyContact, SOSAlert

# =============================================================================
# Emergency contacts (set up by students and parents, editable)
# =============================================================================


@admin.register(EmergencyContact)
class EmergencyContactAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "relationship", "student", "is_primary", "is_active")
    list_filter = ("relationship", "is_primary", "is_active")
    search_fields = (
        "name",
        "phone",
        "student__user__full_name",
        "student__user__phone_number",
    )
    list_select_related = ("student__user",)
    autocomplete_fields = ("student", "user")
    readonly_fields = ("id", "created_at", "updated_at")
    fields = (
        "id",
        "student",
        "name",
        "phone",
        "relationship",
        "user",
        "is_primary",
        "is_active",
        "created_at",
        "updated_at",
    )


# =============================================================================
# SOS alerts (raised from the phone, so view-only)
# =============================================================================


@admin.register(SOSAlert)
class SOSAlertAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ("triggered_at", "student", "status", "channel", "contact", "sent_at")
    list_filter = ("status", "channel")
    search_fields = ("student__user__full_name", "student__user__phone_number")
    list_select_related = ("student__user", "contact")
    date_hierarchy = "triggered_at"
    fieldsets = (
        ("Alert", {"fields": ("id", "student", "active_trip", "status", "message")}),
        ("Delivery", {"fields": ("channel", "contact")}),
        ("Location", {"fields": ("point", "accuracy_m")}),
        (
            "Timeline",
            {
                "fields": (
                    "triggered_at",
                    "sent_at",
                    "cancelled_at",
                    "resolved_at",
                    "resolved_by",
                )
            },
        ),
        ("Dates", {"fields": ("created_at", "updated_at")}),
    )
