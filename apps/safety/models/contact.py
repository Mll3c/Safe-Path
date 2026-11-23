from django.conf import settings
from django.db import models
from django.db.models import Q
from phonenumber_field.modelfields import PhoneNumberField

from apps.core.models import ModelWithTimeStamp, UUIDModel


class ContactRelationship(models.TextChoices):
    FATHER = "father", "Father"
    MOTHER = "mother", "Mother"
    GUARDIAN = "guardian", "Guardian"
    SIBLING = "sibling", "Sibling"
    RELATIVE = "relative", "Other relative"
    OTHER = "other", "Other"


class EmergencyContact(ModelWithTimeStamp, UUIDModel):
    """
    Someone who receives a student's SOS alerts. The primary contact,
    normally the parent, also receives the SMS sent when there's no
    internet.
    """

    Relationship = ContactRelationship

    student = models.ForeignKey(
        "accounts.Student",
        on_delete=models.PROTECT,
        related_name="emergency_contacts",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        help_text=(
            "Set when the contact has an account (usually the parent), so "
            "alerts also arrive in the app."
        ),
    )
    name = models.CharField(max_length=150)
    phone = PhoneNumberField()
    relationship = models.CharField(max_length=16, choices=ContactRelationship.choices)
    is_primary = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-is_primary", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["student"],
                condition=Q(is_primary=True, is_active=True),
                name="safety_contact_one_primary_per_student",
            ),
            models.CheckConstraint(
                condition=Q(relationship__in=ContactRelationship.values),
                name="safety_contact_relationship_valid",
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_relationship_display()}) for {self.student}"

    def clean(self):
        super().clean()
        self.name = (self.name or "").strip()
