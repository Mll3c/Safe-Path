from django.contrib.auth.forms import AdminUserCreationForm

from .models import User


class UserCreationForm(AdminUserCreationForm):
    """Adds a user from the admin, with a password they can sign in with."""

    class Meta(AdminUserCreationForm.Meta):
        model = User
        fields = (
            "phone_number",
            "full_name",
            "email",
            "role",
        )
