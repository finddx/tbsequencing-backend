from typing import Any

from django.db import models as m
from django.db.models.functions import MD5


class Variant(m.Model):
    """Variants model."""

    objects: m.Manager

    variant_id = m.BigAutoField(primary_key=True)
    chromosome = m.CharField(max_length=8_192)
    position = m.IntegerField(db_index=True)
    reference_nucleotide = m.TextField()
    alternative_nucleotide = m.CharField(max_length=8_192)

    annotations: Any  # RelatedManager[Annotation]
    grades: Any  # RelatedManager[VariantGrade]

    class Meta:
        """Variant model options."""

        constraints = [
            m.UniqueConstraint(
                "chromosome",
                "position",
                MD5("reference_nucleotide"),
                MD5("alternative_nucleotide"),
                name="variant_chr_pos_ref_alt_uniq",
            ),
        ]
