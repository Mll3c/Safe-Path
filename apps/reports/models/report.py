from django.conf import settings
from django.db import models
from django.db.models import F, Q
from django.utils import timezone

from apps.core.models import ModelWithTimeStamp, UUIDModel


class ReportPeriod(models.TextChoices):
    WEEKLY = "weekly", "Weekly"
    MONTHLY = "monthly", "Monthly"


class Report(ModelWithTimeStamp, UUIDModel):
    """
    A weekly or monthly summary for a parent or an institution: trips,
    arrivals, delays, deviations, alerts and events. It covers one
    student, one group, or one student within one group, and includes
    only what the recipient is allowed to see.
    """

    Period = ReportPeriod

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="reports",
    )
    student = models.ForeignKey(
        "accounts.Student",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="reports",
    )
    group = models.ForeignKey(
        "groups.Group",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="reports",
    )

    period_type = models.CharField(max_length=16, choices=ReportPeriod.choices)
    period_start = models.DateField()
    period_end = models.DateField()

    summary = models.JSONField(
        default=dict,
        blank=True,
        help_text="Counts of trips, arrivals, delays, deviations, alerts and events.",
    )
    generated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-period_start"]
        constraints = [
            models.CheckConstraint(
                condition=Q(period_type__in=ReportPeriod.values),
                name="reports_report_period_type_valid",
            ),
            models.CheckConstraint(
                condition=Q(period_end__gte=F("period_start")),
                name="reports_report_period_ends_after_start",
            ),
            models.CheckConstraint(
                condition=Q(student__isnull=False) | Q(group__isnull=False),
                name="reports_report_has_subject",
            ),
            # One report per recipient, subject and period. Empty student
            # or group count as equal, so a group report isn't duplicated.
            models.UniqueConstraint(
                fields=["recipient", "student", "group", "period_type", "period_start"],
                nulls_distinct=False,
                name="reports_report_one_per_period",
            ),
        ]

    def __str__(self):
        subject = self.student or self.group
        return f"{self.get_period_type_display()} report – {subject} – {self.period_start}"
