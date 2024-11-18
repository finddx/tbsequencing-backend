from django.apps import AppConfig


class ApiConfig(AppConfig):
    """Config class for API app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "api"
