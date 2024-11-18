from django.db import models


class Contributor(models.Model):
    """Personal info about package data contributor."""

    objects: models.Manager

    first_name = models.CharField(max_length=1024)
    last_name = models.CharField(max_length=1024)
    role = models.CharField(max_length=1024)

    package = models.ForeignKey(
        "Package",
        on_delete=models.CASCADE,
        related_name="contributors",
    )
