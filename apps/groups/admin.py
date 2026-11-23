from django.contrib import admin

from .models import Group, GroupMembership, GroupPermission, MembershipPermission

# =============================================================================
# Permissions (platform-managed, editable)
# =============================================================================


@admin.register(GroupPermission)
class GroupPermissionAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_active", "sort_order")
    list_editable = ("is_active", "sort_order")
    list_filter = ("is_active",)
    search_fields = ("name", "code")
    prepopulated_fields = {"code": ("name",)}


# =============================================================================
# Groups
# =============================================================================


class GroupMembershipInline(admin.TabularInline):
    model = GroupMembership
    fields = ("student", "status", "requested_at", "joined_at", "ended_at")
    autocomplete_fields = ("student",)
    extra = 0
    show_change_link = True


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "owner",
        "status",
        "invite_code",
        "invite_code_expires_at",
        "created_at",
    )
    list_filter = ("status",)
    search_fields = (
        "name",
        "invite_code",
        "parent__user__full_name",
        "parent__user__phone_number",
        "institution__name",
    )
    list_select_related = ("parent__user", "institution")
    autocomplete_fields = ("parent", "institution")
    readonly_fields = ("id", "created_at", "updated_at")
    fieldsets = (
        ("Group", {"fields": ("id", "name", "status")}),
        (
            "Owner",
            {
                "fields": ("parent", "institution"),
                "description": "Fill in exactly one: the parent or the institution.",
            },
        ),
        ("Invitation", {"fields": ("invite_code", "invite_code_expires_at")}),
        ("Dates", {"fields": ("created_at", "updated_at")}),
    )
    inlines = [GroupMembershipInline]

    @admin.display(description="Owner")
    def owner(self, obj):
        return obj.owner


# =============================================================================
# Memberships
# =============================================================================


class MembershipPermissionInline(admin.TabularInline):
    model = MembershipPermission
    fields = ("permission", "created_at")
    readonly_fields = ("created_at",)
    autocomplete_fields = ("permission",)
    extra = 0


@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ("student", "group", "status", "requested_at", "joined_at")
    list_filter = ("status",)
    search_fields = (
        "group__name",
        "student__user__full_name",
        "student__user__phone_number",
    )
    list_select_related = ("group", "student__user")
    autocomplete_fields = ("group", "student")
    readonly_fields = ("id", "created_at", "updated_at")
    fields = (
        "id",
        "group",
        "student",
        "status",
        "requested_at",
        "joined_at",
        "ended_at",
        "created_at",
        "updated_at",
    )
    inlines = [MembershipPermissionInline]
