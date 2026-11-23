import secrets

from django.db import models
from django.db.models import Q
from django.utils import timezone

from apps.core.models import ModelWithTimeStamp, UUIDModel

# No 0/O or 1/I, so a code read aloud or copied by hand isn't misread.
INVITE_CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
INVITE_CODE_LENGTH = 8


def generate_invite_code():
    return "".join(
        secrets.choice(INVITE_CODE_ALPHABET) for _ in range(INVITE_CODE_LENGTH)
    )


class GroupStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    ARCHIVED = "archived", "Archived"


class Group(ModelWithTimeStamp, UUIDModel):
    """
    A family group created by a parent, or a class group created by an
    institution. Students join with the invite code.
    """

    Status = GroupStatus

    name = models.CharField(max_length=150)

    # --- Owner: exactly one of the two ------------------------------------
    parent = models.ForeignKey(
        "accounts.Parent",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="groups",
    )
    institution = models.ForeignKey(
        "accounts.Institution",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="groups",
    )

    # --- Invitation -------------------------------------------------------
    invite_code = models.CharField(
        max_length=16,
        unique=True,
        default=generate_invite_code,
        help_text="Shared with students so they can ask to join.",
    )
    invite_code_expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Empty means the code doesn't expire.",
    )

    status = models.CharField(
        max_length=16,
        choices=GroupStatus.choices,
        default=GroupStatus.ACTIVE,
    )

    class Meta:
        ordering = ["name"]
        constraints = [
            models.CheckConstraint(
                condition=Q(status__in=GroupStatus.values),
                name="groups_group_status_valid",
            ),
            models.CheckConstraint(
                condition=(
                    Q(parent__isnull=False, institution__isnull=True)
                    | Q(parent__isnull=True, institution__isnull=False)
                ),
                name="groups_group_exactly_one_owner",
            ),
        ]

    def __str__(self):
        return self.name

    @property
    def owner(self):
        return self.parent or self.institution

    @property
    def is_invite_code_expired(self):
        return (
            self.invite_code_expires_at is not None
            and timezone.now() >= self.invite_code_expires_at
        )

    def clean(self):
        super().clean()
        self.name = (self.name or "").strip()
