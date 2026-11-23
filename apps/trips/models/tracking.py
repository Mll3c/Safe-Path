from django.contrib.gis.db import models as gis_models
from django.db import models
from django.db.models import Q

from apps.core.models import ModelWithTimeStamp, UUIDModel

from .active_trip import ActiveTrip


class LocationPoint(UUIDModel):
    """
    One GPS reading during an active trip (locaionHistory in the ERD).

    The phone generates the id. Points recorded offline are uploaded
    later, often more than once after a dropped connection, and a known
    id is simply skipped, so nothing is stored twice.
    """

    active_trip = models.ForeignKey(
        ActiveTrip,
        on_delete=models.PROTECT,
        related_name="locations",
    )
    point = gis_models.PointField(srid=4326)
    accuracy_m = models.FloatField(
        null=True,
        blank=True,
        help_text="GPS accuracy radius in metres, as reported by the phone.",
    )
    speed_mps = models.FloatField(null=True, blank=True)
    battery_level = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Phone battery percentage, 0–100.",
    )

    recorded_at = models.DateTimeField(help_text="Phone time of the reading.")
    received_at = models.DateTimeField(auto_now_add=True)
    recorded_offline = models.BooleanField(
        default=False,
        help_text="Stored on the phone without internet and synced later.",
    )

    class Meta:
        ordering = ["recorded_at"]
        indexes = [
            models.Index(
                fields=["active_trip", "recorded_at"],
                name="trips_location_trip_time_idx",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(battery_level__isnull=True) | Q(battery_level__lte=100),
                name="trips_location_battery_level_valid",
            ),
        ]

    def __str__(self):
        return f"{self.active_trip_id} @ {self.recorded_at:%Y-%m-%d %H:%M:%S}"


class TripEventType(models.TextChoices):
    STARTED = "started", "Trip started"
    LEFT_START = "left_start", "Left the start point"
    ARRIVED = "arrived", "Arrived"
    ENDED = "ended", "Trip ended"
    DELAYED = "delayed", "Delayed"
    ROUTE_DEVIATION = "route_deviation", "Route deviation"
    UNUSUAL_STOP = "unusual_stop", "Unusual stop"
    CONNECTION_LOST = "connection_lost", "Connection lost"
    CONNECTION_RESTORED = "connection_restored", "Connection restored"
    LOW_BATTERY = "low_battery", "Low battery"


class EventSeverity(models.TextChoices):
    INFO = "info", "Info"
    WARNING = "warning", "Warning"
    CRITICAL = "critical", "Critical"


class EventSource(models.TextChoices):
    DEVICE = "device", "Detected on the phone"
    RULE = "rule", "Server rule"
    MODEL = "model", "Anomaly-detection model"


class TripEvent(ModelWithTimeStamp, UUIDModel):
    """
    Something that happened during an active trip, including the results
    of the analysis (deviations, delays, unusual stops). Alerts are sent
    from these events.

    The id may come from the phone, for events detected offline.
    """

    Type = TripEventType
    Severity = EventSeverity
    Source = EventSource

    active_trip = models.ForeignKey(
        ActiveTrip,
        on_delete=models.PROTECT,
        related_name="events",
    )
    event_type = models.CharField(max_length=32, choices=TripEventType.choices)
    severity = models.CharField(
        max_length=16,
        choices=EventSeverity.choices,
        default=EventSeverity.INFO,
    )
    source = models.CharField(max_length=16, choices=EventSource.choices)
    description = models.TextField(blank=True)
    point = gis_models.PointField(srid=4326, null=True, blank=True)
    occurred_at = models.DateTimeField()

    class Meta:
        ordering = ["occurred_at"]
        indexes = [
            models.Index(
                fields=["active_trip", "occurred_at"],
                name="trips_event_trip_time_idx",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(event_type__in=TripEventType.values),
                name="trips_event_type_valid",
            ),
            models.CheckConstraint(
                condition=Q(severity__in=EventSeverity.values),
                name="trips_event_severity_valid",
            ),
            models.CheckConstraint(
                condition=Q(source__in=EventSource.values),
                name="trips_event_source_valid",
            ),
        ]

    def __str__(self):
        return f"{self.get_event_type_display()} – {self.active_trip}"
