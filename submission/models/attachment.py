from uuid import uuid4

from django.db import models


def uniq_name_attachment(instance, filename):  # pylint: disable=unused-argument
    """Generate unique attachment name, preserving file extension."""
    ext = filename.split(".", 1)[-1]
    return f"{uuid4().hex}.{ext}"


class Attachment(models.Model):
    """S3 object info, such as filename, directory, size, etc."""

    objects: models.Manager

    class Type(models.TextChoices):
        """Attachment type enum."""

        MIC = "MIC"
        PDS = "PDS"
        OTHER = "OTHER"

    created_at = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=32, choices=Type.choices, default=Type.OTHER)

    file = models.FileField(upload_to=uniq_name_attachment)
    """Attachments will use default S3 storage."""

    size = models.BigIntegerField(null=True)
    """File size in bytes."""

    original_filename = models.CharField(max_length=1024, null=True)
    """Original filename, by which the attachment was uploaded."""

    package = models.ForeignKey("Package", models.CASCADE, related_name="attachments")

    def __str__(self):
        """Represent instance of an attachment."""
        return f"<Attachment #{self.pk} {self.type} {self.original_filename}>"
