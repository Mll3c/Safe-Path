from django.db import models

from apps.core.models import UUIDModel


class GroupPermission(UUIDModel):
    """
    Platform-managed list of what a group may see or receive about a
    member, for example ``view_live_location``, ``view_trip_history``,
    ``receive_trip_alerts``, ``receive_sos_alerts``,
    ``view_geofence_events`` and ``view_reports``.

    Each membership grants its own set, so a family group and a school
    group can see different things about the same student.
    """

    code = models.SlugField(
        max_length=64,
        unique=True,
        help_text="Stable identifier used in code. Don't change it once in use.",
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name
