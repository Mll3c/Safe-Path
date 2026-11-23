from django.db import models
from django.db.models import F, Q

from apps.core.models import ModelWithTimeStamp, UUIDModel

from .trip import Trip


class ActiveTripStatus(models.TextChoices):
    IN_PROGRESS = "in_progress", "In progress"
    ARRIVED = "arrived", "Arrived"
    ENDED = "ended", "Ended without arriving"


class ActiveTrip(ModelWithTimeStamp, UUIDModel):
    """
    One run of a trip by one student. Tracking runs while it is in
    progress and the student can't stop it. It ends when the student
    stays inside the destination geofence long enough, or when another
    end condition is met.
    """

    Status = ActiveTripStatus

    trip = models.ForeignKey(
        Trip,
        on_delete=models.PROTECT,
        related_name="runs",
    )
    student = models.ForeignKey(
        "accounts.Student",
        on_delete=models.PROTECT,
        related_name="active_trips",
    )
    status = models.CharField(
        max_length=16,
        choices=ActiveTripStatus.choices,
        default=ActiveTripStatus.IN_PROGRESS,
    )

    started_at = models.DateTimeField(
        help_text="Phone time when the student tapped Start.",
    )
    arrived_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    last_seen_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=(
            "When the server last heard from the student's phone. Used to "
            "raise connection-lost alerts."
        ),
    )

    class Meta:
        ordering = ["-started_at"]
        indexes = [
            models.Index(
                fields=["student", "started_at"],
                name="trips_activetrip_student_idx",
            ),
        ]
        constraints = [
            # Tracking follows one trip at a time.
            models.UniqueConstraint(
                fields=["student"],
                condition=Q(status=ActiveTripStatus.IN_PROGRESS),
                name="trips_activetrip_one_in_progress_per_student",
            ),
            models.CheckConstraint(
                condition=Q(status__in=ActiveTripStatus.values),
                name="trips_activetrip_status_valid",
            ),
            models.CheckConstraint(
                condition=~Q(status=ActiveTripStatus.ARRIVED) | Q(arrived_at__isnull=False),
                name="trips_activetrip_arrived_has_arrived_at",
            ),
            models.CheckConstraint(
                condition=(
                    Q(status=ActiveTripStatus.IN_PROGRESS, ended_at__isnull=True)
                    | (~Q(status=ActiveTripStatus.IN_PROGRESS) & Q(ended_at__isnull=False))
                ),
                name="trips_activetrip_ended_at_matches_status",
            ),
            models.CheckConstraint(
                condition=Q(ended_at__isnull=True) | Q(ended_at__gte=F("started_at")),
                name="trips_activetrip_ends_after_start",
            ),
        ]

    def __str__(self):
        return f"{self.trip} – {self.student} ({self.started_at:%Y-%m-%d %H:%M})"
