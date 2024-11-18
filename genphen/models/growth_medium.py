from typing import Any

from django.db import models as m


class GrowthMedium(m.Model):
    """Growth medium model."""

    objects: m.Manager

    medium_id = m.AutoField(primary_key=True)
    medium_name = m.CharField(max_length=8_192, unique=True)

    pds_tests: Any  # RelatedManager[PDSTest]
