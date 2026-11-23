from django.conf import settings
from django.contrib.gis.db import models as gis_models
from django.db import models
from django.db.models import Q
from django.utils import timezone

from apps.core.models import ModelWithTimeStamp, UUIDModel


class TripStatus(models.TextChoices):
    ACTIVE = "active", "Available"
    ARCHIVED = "archived", "Archived"


class Trip(ModelWithTimeStamp, UUIDModel):
    """
    A planned, reusable trip such as "Home → School", created by a
    parent for a group. Each time a student runs it, an ActiveTrip is
    created.
    """

    Status = TripStatus

    group = models.ForeignKey(
        "groups.Group",
        on_delete=models.PROTECT,
        related_name="trips",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="+",
    )
    name = models.CharField(max_length=150)

    # --- Route ------------------------------------------------------------
    start_label = models.CharField(
        max_length=255,
        blank=True,
        help_text="How the start point is shown, for example 'Home'.",
    )
    start_point = gis_models.PointField(srid=4326)
    destination_label = models.CharField(max_length=255, blank=True)
    destination_point = gis_models.PointField(srid=4326)
    expected_route = gis_models.LineStringField(
        srid=4326,
        null=True,
        blank=True,
        help_text=(
            "Calculated from the start and destination. Locations recorded "
            "during a run are compared with it to detect deviations."
        ),
    )
    expected_duration = models.DurationField(null=True, blank=True)

    status = models.CharField(
        max_length=16,
        choices=TripStatus.choices,
        default=TripStatus.ACTIVE,
    )
    students = models.ManyToManyField(
        "accounts.Student",
        through="TripStudent",
        related_name="trips",
        blank=True,
    )

    class Meta:
        ordering = ["name"]
        constraints = [
            models.CheckConstraint(
                condition=Q(status__in=TripStatus.values),
                name="trips_trip_status_valid",
            ),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        self.name = (self.name or "").strip()


class TripStudentStatus(models.TextChoices):
    ASSIGNED = "assigned", "Assigned"
    REMOVED = "removed", "Removed"


class TripStudent(ModelWithTimeStamp, UUIDModel):
    """A student allowed to start a trip."""

    Status = TripStudentStatus

    trip = models.ForeignKey(
        Trip,
        on_delete=models.PROTECT,
        related_name="assignments",
    )
    student = models.ForeignKey(
        "accounts.Student",
        on_delete=models.PROTECT,
        related_name="trip_assignments",
    )
    status = models.CharField(
        max_length=16,
        choices=TripStudentStatus.choices,
        default=TripStudentStatus.ASSIGNED,
    )
    assigned_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["trip", "student"],
                name="trips_tripstudent_trip_student_uniq",
            ),
            models.CheckConstraint(
                condition=Q(status__in=TripStudentStatus.values),
                name="trips_tripstudent_status_valid",
            ),
        ]

    def __str__(self):
        return f"{self.student} on {self.trip}"
