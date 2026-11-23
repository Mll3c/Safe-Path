from django.db import models
from django.db.models import Q
from django.utils import timezone

from apps.core.models import ModelWithTimeStamp, UUIDModel

from .group import Group
from .permission import GroupPermission


class MembershipStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    ACTIVE = "active", "Active"
    REJECTED = "rejected", "Rejected"
    LEFT = "left", "Left"
    REMOVED = "removed", "Removed"


# Statuses that still link the student to the group.
OPEN_STATUSES = [MembershipStatus.PENDING, MembershipStatus.ACTIVE]
# Statuses that end a membership that was active.
ENDED_STATUSES = [MembershipStatus.LEFT, MembershipStatus.REMOVED]


class GroupMembership(ModelWithTimeStamp, UUIDModel):
    """
    A student's link to a group (STUDENT_GROUP in the ERD). It starts as
    pending after the student enters the invite code. The group sees
    nothing about the student until the membership is active.
    """

    Status = MembershipStatus

    group = models.ForeignKey(
        Group,
        on_delete=models.PROTECT,
        related_name="memberships",
    )
    student = models.ForeignKey(
        "accounts.Student",
        on_delete=models.PROTECT,
        related_name="group_memberships",
    )
    status = models.CharField(
        max_length=16,
        choices=MembershipStatus.choices,
        default=MembershipStatus.PENDING,
    )
    permissions = models.ManyToManyField(
        GroupPermission,
        through="MembershipPermission",
        related_name="memberships",
        blank=True,
    )

    requested_at = models.DateTimeField(default=timezone.now)
    joined_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the membership became active.",
    )
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-requested_at"]
        constraints = [
            # A student can be in a group once. Old rejected or ended
            # memberships stay as history and don't block a new request.
            models.UniqueConstraint(
                fields=["group", "student"],
                condition=Q(status__in=OPEN_STATUSES),
                name="groups_membership_one_open_per_student",
            ),
            models.CheckConstraint(
                condition=Q(status__in=MembershipStatus.values),
                name="groups_membership_status_valid",
            ),
            models.CheckConstraint(
                condition=~Q(status=MembershipStatus.ACTIVE) | Q(joined_at__isnull=False),
                name="groups_membership_active_has_joined_at",
            ),
            models.CheckConstraint(
                condition=(
                    Q(status__in=ENDED_STATUSES, ended_at__isnull=False)
                    | (~Q(status__in=ENDED_STATUSES) & Q(ended_at__isnull=True))
                ),
                name="groups_membership_ended_at_matches_status",
            ),
        ]

    def __str__(self):
        return f"{self.student} in {self.group} ({self.status})"


class MembershipPermission(ModelWithTimeStamp, UUIDModel):
    """One permission granted by one membership."""

    membership = models.ForeignKey(
        GroupMembership,
        on_delete=models.CASCADE,
        related_name="permission_grants",
    )
    permission = models.ForeignKey(
        GroupPermission,
        on_delete=models.PROTECT,
        related_name="grants",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["membership", "permission"],
                name="groups_membershippermission_uniq",
            ),
        ]

    def __str__(self):
        return f"{self.permission} – {self.membership}"
