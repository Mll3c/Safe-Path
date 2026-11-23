from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.gis.admin import GISModelAdmin

from .forms import UserCreationForm
from .models import Institution, Parent, Student, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = UserCreationForm

    list_display = (
        "phone_number",
        "full_name",
        "email",
        "role",
        "is_staff",
        "is_active",
    )
    list_filter = ("role", "is_staff", "is_superuser", "is_active")
    search_fields = ("phone_number", "full_name", "email")
    readonly_fields = (
        "id",
        "last_login",
        "created_at",
        "updated_at",
    )
    ordering = ("full_name",)

    fieldsets = (
        (
            "Identity",
            {
                "fields": (
                    "phone_number",
                    "email",
                    "password",
                )
            },
        ),
        (
            "Profile",
            {"fields": ("full_name", "role")},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Dates",
            {
                "fields": (
                    "last_login",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    add_fieldsets = (
        (
            "Create User",
            {
                "fields": (
                    "phone_number",
                    "full_name",
                    "email",
                    "role",
                    "usable_password",
                    "password1",
                    "password2",
                )
            },
        ),
    )


# =============================================================================
# Profiles
# =============================================================================


class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone_number", "created_at")
    search_fields = ("user__full_name", "user__phone_number", "user__email")
    list_select_related = ("user",)
    autocomplete_fields = ("user",)
    readonly_fields = ("id", "created_at", "updated_at")

    @admin.display(description="Phone number", ordering="user__phone_number")
    def phone_number(self, obj):
        return obj.user.phone_number


@admin.register(Parent)
class ParentAdmin(ProfileAdmin):
    pass


@admin.register(Student)
class StudentAdmin(ProfileAdmin):
    pass


@admin.register(Institution)
class InstitutionAdmin(GISModelAdmin):
    list_display = ("name", "user", "phone", "created_at")
    search_fields = ("name", "phone", "user__full_name", "user__phone_number")
    list_select_related = ("user",)
    autocomplete_fields = ("user",)
    readonly_fields = ("id", "created_at", "updated_at")
    fieldsets = (
        ("Institution", {"fields": ("id", "name", "user", "phone")}),
        ("Location", {"fields": ("address", "location")}),
        ("Dates", {"fields": ("created_at", "updated_at")}),
    )
