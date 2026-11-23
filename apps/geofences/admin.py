from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin

from apps.core.admin import ReadOnlyAdminMixin

from .models import Geofence, GeofenceEvent, InstitutionGeofence, TripGeofence

# =============================================================================
# Geofences (drawn by institutions and parents, editable)
# =============================================================================


class InstitutionGeofenceInline(admin.TabularInline):
    model = InstitutionGeofence
    fields = ("institution",)
    autocomplete_fields = ("institution",)
    extra = 0


class TripGeofenceInline(admin.TabularInline):
    model = TripGeofence
    fields = ("trip", "purpose")
    autocomplete_fields = ("trip",)
    extra = 0


@admin.register(Geofence)
class GeofenceAdmin(GISModelAdmin):
    list_display = ("name", "radius_m", "dwell_seconds", "created_at")
    search_fields = ("name",)
    autocomplete_fields = ("created_by",)
    readonly_fields = ("id", "created_at", "updated_at")
    fieldsets = (
        ("Geofence", {"fields": ("id", "name", "created_by")}),
        ("Area", {"fields": ("center", "radius_m", "dwell_seconds")}),
        ("Dates", {"fields": ("created_at", "updated_at")}),
    )
    inlines = [InstitutionGeofenceInline, TripGeofenceInline]


# =============================================================================
# Crossings (recorded by the phones, so view-only)
# =============================================================================


@admin.register(GeofenceEvent)
class GeofenceEventAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ("occurred_at", "event_type", "student", "geofence", "active_trip")
    list_filter = ("event_type",)
    search_fields = (
        "geofence__name",
        "student__user__full_name",
        "student__user__phone_number",
    )
    list_select_related = ("geofence", "student__user", "active_trip__trip")
    date_hierarchy = "occurred_at"
