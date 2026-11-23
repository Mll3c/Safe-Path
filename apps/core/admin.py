class ReadOnlyAdminMixin:
    """
    View-only admin, for data that must change only through services
    (which enforce business rules).
    Works for both model admins and inlines.
    """

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
