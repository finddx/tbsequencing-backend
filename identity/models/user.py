from typing import Any

from django.contrib.auth.models import User as BaseUser, UserManager as BaseUserManager


class UserManager(BaseUserManager):
    """Custom User manager with more convenient helper functions."""

    def admins_on_duty(self):
        """Filter staff users that should be notified about events in application."""
        return self.filter(
            is_staff=True,
            email__isnull=False,
        )


class User(BaseUser):
    """
    Custom User class with advanced Manager.

    The class is created mostly for its custom manager.
    """

    objects = UserManager()
    packages: Any  # RelatedManager[Package]

    class Meta:
        """Specify that the model is a proxy."""

        proxy = True

    def __str__(self):
        """Show user full name if exists, else username."""
        if not self.first_name and not self.last_name:
            return self.username
        return f"{self.first_name} {self.last_name}"
