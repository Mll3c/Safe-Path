from django.conf import settings
from django.contrib.gis.db import models as gis_models
from django.db import models
from django.db.models import Q

from apps.core.models import ModelWithTimeStamp, UUIDModel

from .contact import EmergencyContact


class SOSStatus(models.TextChoices):
    COUNTDOWN = "countdown", "Counting down"
    SENT = "sent", "Sent"
    CANCELLED = "cancelled", "Cancelled"
    RESOLVED = "resolved", "Resolved"


class SOSChannel(models.TextChoices):
    INTERNET = "internet", "Internet"
    SMS = "sms", "SMS"


# Statuses reached after the alert went out.
SENT_STATUSES = [SOSStatus.SENT, SOSStatus.RESOLVED]


class SOSAlert(ModelWithTimeStamp, UUIDModel):
    """
    An SOS raised by a student. After a 10–15 second countdown, which the
    student can cancel, it goes out over the internet, or by SMS from the
    phone when there's no internet.

    The phone generates the id. An alert sent by SMS reaches the server
    only when the phone reconnects, and re-sending it must not create a
    second alert. The location is stored here, not as a link to a
    recorded GPS point, because an SMS alert may have no synced point.
    """

    Status = SOSStatus
    Channel = SOSChannel

    student = models.ForeignKey(
        "accounts.Student",
        on_delete=models.PROTECT,
        related_name="sos_alerts",
    )
    active_trip = models.ForeignKey(
        "trips.ActiveTrip",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="sos_alerts",
    )
    contact = models.ForeignKey(
        EmergencyContact,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="sos_alerts",
        help_text="The contact the alert was sent to.",
    )

    status = models.CharField(
        max_length=16,
        choices=SOSStatus.choices,
        default=SOSStatus.COUNTDOWN,
    )
    channel = models.CharField(
        max_length=16,
        choices=SOSChannel.choices,
        null=True,
        blank=True,
        help_text="How the alert went out. Empty until it is sent.",
    )
    message = models.TextField(blank=True)

    point = gis_models.PointField(srid=4326, null=True, blank=True)
    accuracy_m = models.FloatField(null=True, blank=True)

    triggered_at = models.DateTimeField(help_text="Phone time when SOS was pressed.")
    sent_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )

    class Meta:
        ordering = ["-triggered_at"]
        verbose_name = "SOS alert"
        indexes = [
            models.Index(
                fields=["status", "triggered_at"],
                name="safety_sos_status_idx",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(status__in=SOSStatus.values),
                name="safety_sos_status_valid",
            ),
            models.CheckConstraint(
                condition=Q(channel__isnull=True) | Q(channel__in=SOSChannel.values),
                name="safety_sos_channel_valid",
            ),
            models.CheckConstraint(
                condition=(
                    ~Q(status__in=SENT_STATUSES)
                    | Q(sent_at__isnull=False, channel__isnull=False)
                ),
                name="safety_sos_sent_has_time_and_channel",
            ),
            models.CheckConstraint(
                condition=~Q(status=SOSStatus.CANCELLED) | Q(cancelled_at__isnull=False),
                name="safety_sos_cancelled_has_time",
            ),
            models.CheckConstraint(
                condition=~Q(status=SOSStatus.RESOLVED) | Q(resolved_at__isnull=False),
                name="safety_sos_resolved_has_time",
            ),
        ]

    def __str__(self):
        return f"SOS from {self.student} ({self.status}, {self.triggered_at:%Y-%m-%d %H:%M})"
