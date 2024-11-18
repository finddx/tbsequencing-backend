from django.apps import AppConfig


class SubmissionConfig(AppConfig):
    """Config class for Submission API app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "submission"

    # noinspection PyUnresolvedReferences
    def ready(self):
        """Ready to start signals?"""
        import submission.signals  # pylint: disable-msg=W0611, C0415
