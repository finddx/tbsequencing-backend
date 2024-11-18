from typing import Any

from django.db import models


class PDSAssessmentMethod(models.Model):
    """Phenotypic drug susceptibility assessment methods."""

    objects: models.Manager

    method_id = models.AutoField(primary_key=True)
    method_name = models.CharField(unique=True, max_length=1024)

    pds_tests: Any  # RelatedManager[PDSTest]
