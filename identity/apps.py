from django.apps import AppConfig


class IdentityConfig(AppConfig):
    """Identity app config."""

    name = "identity"

    def ready(self):
        """Import app signal handlers."""
        from . import signals  # pylint: disable=import-outside-toplevel,unused-import
