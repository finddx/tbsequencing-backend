from django.db import models


class Country(models.Model):
    """Country list from pycountry module."""

    objects: models.Manager

    three_letters_code = models.CharField(
        max_length=3,
        unique=True,
        null=False,
        primary_key=True,
    )
    country_id = models.IntegerField(unique=True)
    two_letters_code = models.CharField(max_length=2, unique=True)
    country_usual_name = models.CharField(max_length=1024)
    country_official_name = models.CharField(max_length=1024, null=True)

    def __str__(self):
        """Return string representation of a model."""
        return f"{self.three_letters_code} {self.country_usual_name}"
