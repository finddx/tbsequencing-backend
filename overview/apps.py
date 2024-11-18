from django.apps import AppConfig
from django.db.models import Field

from .lookups import Overlaps


class OverviewConfig(AppConfig):
    """Overview app config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "overview"

    def ready(self):
        """Do app startup, one-time stuff."""
        Field.register_lookup(Overlaps)
