from django.contrib.gis.db import models as gis_models
from django.db import models
from django.db.models import Q

from apps.core.models import ModelWithTimeStamp, UUIDModel

from .geofence import Geofence


class GeofenceEventType(models.TextChoices):
    ENTERED = "entered", "Entered"
    EXITED = "exited", "Exited"


class GeofenceEvent(ModelWithTimeStamp, UUIDModel):
    """
    A student entering or leaving a geofence. An institution sees these
    entry and exit times, never the student's live location.

    The id may come from the phone, for crossings detected offline.
    """

    Type = GeofenceEventType

    geofence = models.ForeignKey(
        Geofence,
        on_delete=models.PROTECT,
        related_name="events",
    )
    student = models.ForeignKey(
        "accounts.Student",
        on_delete=models.PROTECT,
        related_name="geofence_events",
    )
    active_trip = models.ForeignKey(
        "trips.ActiveTrip",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="geofence_events",
        help_text=(
            "The run during which the crossing was detected. Empty if it "
            "was detected outside a trip."
        ),
    )
    event_type = models.CharField(max_length=16, choices=GeofenceEventType.choices)
    point = gis_models.PointField(srid=4326, null=True, blank=True)
    occurred_at = models.DateTimeField()

    class Meta:
        ordering = ["-occurred_at"]
        indexes = [
            # An institution's daily entry and exit list.
            models.Index(
                fields=["geofence", "occurred_at"],
                name="geofences_event_fence_time_idx",
            ),
            models.Index(
                fields=["student", "occurred_at"],
                name="geofences_event_student_idx",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(event_type__in=GeofenceEventType.values),
                name="geofences_event_type_valid",
            ),
        ]

    def __str__(self):
        return f"{self.student} {self.event_type} {self.geofence.name}"
