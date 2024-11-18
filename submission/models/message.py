from django.db import models

from identity.models import User
from .package import Package


class Message(models.Model):
    """Messages between Admin and Delegate."""

    objects: models.Manager

    class Meta:
        """Messages model options."""

        ordering = ("timestamp",)

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_messages",
    )
    content = models.TextField(max_length=2000, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    package = models.ForeignKey(
        Package,
        on_delete=models.CASCADE,
        related_name="messages",
    )

    def __str__(self):
        """To show namespace in admin page."""
        return f"From: {self.sender}"
