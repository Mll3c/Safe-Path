from django.conf import settings
from django.db import models
from django.db.models import Q

from apps.core.models import ModelWithTimeStamp, UUIDModel


class NotificationType(models.TextChoices):
    TRIP = "trip", "Trip event"
    GEOFENCE = "geofence", "Geofence entry or exit"
    SOS = "sos", "SOS alert"
    GROUP = "group", "Group activity"
    REPORT = "report", "Report ready"
    SYSTEM = "system", "System"


class NotificationChannel(models.TextChoices):
    PUSH = "push", "Push"
    SMS = "sms", "SMS"
    IN_APP = "in_app", "In app only"


class NotificationStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    SENT = "sent", "Sent"
    FAILED = "failed", "Failed"


class Notification(ModelWithTimeStamp, UUIDModel):
    """
    A message to one user. Trip, geofence and SOS notifications point at
    the event that caused them, and the type says which one.
    """

    Type = NotificationType
    Channel = NotificationChannel
    Status = NotificationStatus

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="notifications",
    )
    notification_type = models.CharField(max_length=16, choices=NotificationType.choices)

    # --- What caused it: at most one, matching the type ---------------------
    trip_event = models.ForeignKey(
        "trips.TripEvent",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="notifications",
    )
    geofence_event = models.ForeignKey(
        "geofences.GeofenceEvent",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="notifications",
    )
    sos_alert = models.ForeignKey(
        "safety.SOSAlert",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="notifications",
    )

    title = models.CharField(max_length=150)
    message = models.TextField()

    channel = models.CharField(
        max_length=16,
        choices=NotificationChannel.choices,
        default=NotificationChannel.PUSH,
    )
    status = models.CharField(
        max_length=16,
        choices=NotificationStatus.choices,
        default=NotificationStatus.PENDING,
    )
    sent_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            # A user's notification list, newest first.
            models.Index(
                fields=["recipient", "created_at"],
                name="notifications_recipient_idx",
            ),
            # The sending queue.
            models.Index(
                fields=["status", "created_at"],
                name="notifications_queue_idx",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(notification_type__in=NotificationType.values),
                name="notifications_type_valid",
            ),
            models.CheckConstraint(
                condition=Q(channel__in=NotificationChannel.values),
                name="notifications_channel_valid",
            ),
            models.CheckConstraint(
                condition=Q(status__in=NotificationStatus.values),
                name="notifications_status_valid",
            ),
            models.CheckConstraint(
                condition=(
                    Q(
                        notification_type=NotificationType.TRIP,
                        trip_event__isnull=False,
                        geofence_event__isnull=True,
                        sos_alert__isnull=True,
                    )
                    | Q(
                        notification_type=NotificationType.GEOFENCE,
                        trip_event__isnull=True,
                        geofence_event__isnull=False,
                        sos_alert__isnull=True,
                    )
                    | Q(
                        notification_type=NotificationType.SOS,
                        trip_event__isnull=True,
                        geofence_event__isnull=True,
                        sos_alert__isnull=False,
                    )
                    | Q(
                        notification_type__in=[
                            NotificationType.GROUP,
                            NotificationType.REPORT,
                            NotificationType.SYSTEM,
                        ],
                        trip_event__isnull=True,
                        geofence_event__isnull=True,
                        sos_alert__isnull=True,
                    )
                ),
                name="notifications_source_matches_type",
            ),
            models.CheckConstraint(
                condition=~Q(status=NotificationStatus.SENT) | Q(sent_at__isnull=False),
                name="notifications_sent_has_sent_at",
            ),
        ]

    def __str__(self):
        return f"{self.title} → {self.recipient}"

    @property
    def is_read(self):
        return self.read_at is not None
