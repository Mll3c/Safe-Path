from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.contrib.gis.db import models as gis_models
from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower

from apps.core.models import ModelWithTimeStamp, UUIDModel

from phonenumber_field.modelfields import PhoneNumberField


class UserRole(models.TextChoices):
    STUDENT = "student", "Student"
    PARENT = "parent", "Parent"
    INSTITUTION = "institution", "Educational institution"


class UserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("Phone number is required.")

        user = self.model(phone_number=phone_number, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(phone_number, password, **extra_fields)


class User(ModelWithTimeStamp, UUIDModel, AbstractBaseUser, PermissionsMixin):
    """
    One login for every kind of account. ``role`` says which profile
    (Student, Parent or Institution) holds the rest of the account's data.
    People sign in with their phone number or email and a password.
    """

    Role = UserRole

    full_name = models.CharField(max_length=255, null=True, blank=True)

    phone_number = PhoneNumberField(unique=True)
    email = models.EmailField(null=True, blank=True)

    role = models.CharField(
        max_length=16,
        choices=UserRole.choices,
        null=True,
        blank=True,
        help_text="The account type chosen at sign-up. Empty for platform staff.",
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "phone_number"

    class Meta:
        constraints = [
            # Email is a login identifier, so it's unique ignoring case.
            models.UniqueConstraint(
                Lower("email"),
                name="accounts_user_email_ci_unique",
            ),
            models.CheckConstraint(
                condition=Q(role__isnull=True) | Q(role__in=UserRole.values),
                name="accounts_user_role_valid",
            ),
        ]

    def clean(self):
        super().clean()
        self.email = self._normalize_email(self.email)

    def save(self, *args, **kwargs):
        self.email = self._normalize_email(self.email)
        super().save(*args, **kwargs)

    @staticmethod
    def _normalize_email(email):
        email = (email or "").strip()
        return email.lower() or None

    def __str__(self):
        return (
            f"{self.full_name} ({self.phone_number})"
            if self.full_name
            else str(self.phone_number)
        )


# =============================================================================
# Profiles: one per account, matching the user's role
# =============================================================================


class Parent(ModelWithTimeStamp, UUIDModel):
    """A parent or guardian. Creates family groups and trips for their children."""

    user = models.OneToOneField(
        User,
        on_delete=models.PROTECT,
        related_name="parent_profile",
    )

    class Meta:
        ordering = ["user__full_name"]

    def __str__(self):
        return str(self.user)


class Student(ModelWithTimeStamp, UUIDModel):
    """A student. Joins groups, runs trips and is tracked while a trip is active."""

    user = models.OneToOneField(
        User,
        on_delete=models.PROTECT,
        related_name="student_profile",
    )

    class Meta:
        ordering = ["user__full_name"]

    def __str__(self):
        return str(self.user)


class Institution(ModelWithTimeStamp, UUIDModel):
    """
    A school or university. Creates class groups and records when its
    students enter and leave its geofence, without seeing their live location.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.PROTECT,
        related_name="institution_profile",
        help_text="The account that manages the institution.",
    )
    name = models.CharField(max_length=150)
    phone = PhoneNumberField(null=True, blank=True)
    address = models.CharField(
        max_length=255,
        blank=True,
        help_text="Street, building and a landmark.",
    )
    location = gis_models.PointField(srid=4326, null=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        self.name = (self.name or "").strip()
