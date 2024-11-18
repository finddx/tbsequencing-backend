import enum

from django.db import models


class VerdictMixin(models.Model):
    """Mixin class for django model, that adds validation messages storage capabilities."""

    class Meta:
        """VerdictMixin options class."""

        abstract = True

    class VerdictLevel(enum.Enum):
        """Severity of particular verdict message."""

        INFO = "info"
        WARNING = "warning"
        ERROR = "error"

    verdicts = models.JSONField(default=list)

    def add_verdict(self, verdict: str, level: VerdictLevel):
        """
        Add verdict to a model record.

        This verdict could be used later to see, what's wrong with this particular record.
        """
        self.verdicts: list
        self.verdicts.append({"verdict": verdict, "level": level.value})
        self.save()
