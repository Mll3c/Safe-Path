from django.conf import settings
from django.contrib.gis.db import models as gis_models
from django.db import models
from django.db.models import Q

from apps.core.models import ModelWithTimeStamp, UUIDModel


class Geofence(ModelWithTimeStamp, UUIDModel):
    """
    A circle on the map: a centre and a radius. Used for an institution's
    boundary and for a trip's destination. One geofence can be shared,
    for example a school used as the destination of many trips.
    """

    name = models.CharField(max_length=150)
    center = gis_models.PointField(srid=4326)
    radius_m = models.PositiveIntegerField(help_text="Radius in metres.")
    dwell_seconds = models.PositiveIntegerField(
        default=60,
        help_text=(
            "How long a student must stay inside before it counts as "
            "arriving. Stops a student passing by from ending the trip."
        ),
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="+",
    )

    institutions = models.ManyToManyField(
        "accounts.Institution",
        through="InstitutionGeofence",
        related_name="geofences",
        blank=True,
    )
    trips = models.ManyToManyField(
        "trips.Trip",
        through="TripGeofence",
        related_name="geofences",
        blank=True,
    )

    class Meta:
        ordering = ["name"]
        constraints = [
            models.CheckConstraint(
                condition=Q(radius_m__gt=0),
                name="geofences_geofence_radius_positive",
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.radius_m} m)"


class InstitutionGeofence(ModelWithTimeStamp, UUIDModel):
    """An institution's boundary. Entry and exit are recorded against it."""

    institution = models.ForeignKey(
        "accounts.Institution",
        on_delete=models.PROTECT,
        related_name="geofence_links",
    )
    geofence = models.ForeignKey(
        Geofence,
        on_delete=models.PROTECT,
        related_name="institution_links",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["institution", "geofence"],
                name="geofences_institutiongeofence_uniq",
            ),
        ]

    def __str__(self):
        return f"{self.geofence} – {self.institution}"


class TripGeofencePurpose(models.TextChoices):
    START = "start", "Start"
    DESTINATION = "destination", "Destination"
    CHECKPOINT = "checkpoint", "Checkpoint"


class TripGeofence(ModelWithTimeStamp, UUIDModel):
    """A geofence used by a trip. Arrival is detected with the destination one."""

    Purpose = TripGeofencePurpose

    trip = models.ForeignKey(
        "trips.Trip",
        on_delete=models.PROTECT,
        related_name="geofence_links",
    )
    geofence = models.ForeignKey(
        Geofence,
        on_delete=models.PROTECT,
        related_name="trip_links",
    )
    purpose = models.CharField(
        max_length=16,
        choices=TripGeofencePurpose.choices,
        default=TripGeofencePurpose.DESTINATION,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["trip", "geofence"],
                name="geofences_tripgeofence_uniq",
            ),
            models.UniqueConstraint(
                fields=["trip"],
                condition=Q(purpose=TripGeofencePurpose.DESTINATION),
                name="geofences_tripgeofence_one_destination",
            ),
            models.CheckConstraint(
                condition=Q(purpose__in=TripGeofencePurpose.values),
                name="geofences_tripgeofence_purpose_valid",
            ),
        ]

    def __str__(self):
        return f"{self.trip}: {self.purpose} {self.geofence}"
