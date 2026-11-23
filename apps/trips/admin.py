from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin

from apps.core.admin import ReadOnlyAdminMixin
from apps.geofences.models import TripGeofence

from .models import ActiveTrip, LocationPoint, Trip, TripEvent, TripStudent

# =============================================================================
# Trips (set up by parents, editable)
# =============================================================================


class TripStudentInline(admin.TabularInline):
    model = TripStudent
    fields = ("student", "status", "assigned_at")
    autocomplete_fields = ("student",)
    extra = 0


class TripGeofenceInline(admin.TabularInline):
    model = TripGeofence
    fields = ("geofence", "purpose")
    autocomplete_fields = ("geofence",)
    extra = 0


class ActiveTripInline(ReadOnlyAdminMixin, admin.TabularInline):
    model = ActiveTrip
    fields = ("student", "status", "started_at", "arrived_at", "ended_at")
    readonly_fields = fields
    extra = 0
    show_change_link = True
    verbose_name_plural = "runs"


@admin.register(Trip)
class TripAdmin(GISModelAdmin):
    list_display = ("name", "group", "status", "expected_duration", "created_at")
    list_filter = ("status",)
    search_fields = ("name", "group__name", "start_label", "destination_label")
    list_select_related = ("group",)
    autocomplete_fields = ("group", "created_by")
    readonly_fields = ("id", "created_at", "updated_at")
    fieldsets = (
        ("Trip", {"fields": ("id", "name", "group", "created_by", "status")}),
        ("Start", {"fields": ("start_label", "start_point")}),
        ("Destination", {"fields": ("destination_label", "destination_point")}),
        ("Expected route", {"fields": ("expected_route", "expected_duration")}),
        ("Dates", {"fields": ("created_at", "updated_at")}),
    )
    inlines = [TripStudentInline, TripGeofenceInline, ActiveTripInline]


# =============================================================================
# Runs and tracking (recorded by the phones and the server, so view-only)
# =============================================================================


class TripEventInline(ReadOnlyAdminMixin, admin.TabularInline):
    model = TripEvent
    fields = ("occurred_at", "event_type", "severity", "source", "description")
    readonly_fields = fields
    extra = 0
    show_change_link = True


@admin.register(ActiveTrip)
class ActiveTripAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ("trip", "student", "status", "started_at", "arrived_at", "last_seen_at")
    list_filter = ("status",)
    search_fields = (
        "=id",
        "trip__name",
        "student__user__full_name",
        "student__user__phone_number",
    )
    list_select_related = ("trip", "student__user")
    date_hierarchy = "started_at"
    inlines = [TripEventInline]


@admin.register(TripEvent)
class TripEventAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ("occurred_at", "event_type", "severity", "source", "active_trip")
    list_filter = ("event_type", "severity", "source")
    search_fields = ("=active_trip__id", "active_trip__student__user__full_name")
    list_select_related = ("active_trip__trip", "active_trip__student__user")
    date_hierarchy = "occurred_at"


@admin.register(LocationPoint)
class LocationPointAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    """
    Locations are numerous, so they aren't shown inline on the run's page.
    Search by the run's id to see one run's points.
    """

    list_display = (
        "recorded_at",
        "active_trip",
        "accuracy_m",
        "battery_level",
        "recorded_offline",
        "received_at",
    )
    list_filter = ("recorded_offline",)
    search_fields = ("=active_trip__id",)
    list_select_related = ("active_trip__trip", "active_trip__student__user")
    show_full_result_count = False
