from django.db import models as m


class GenotypeResistance(m.Model):
    """Predicted (genotypical) resistance data."""

    objects: m.Manager

    sample = m.ForeignKey(
        "Sample",
        on_delete=m.CASCADE,
        related_name="genotype_resistances",
    )
    drug = m.ForeignKey(
        "genphen.Drug",
        on_delete=m.CASCADE,
        related_name="genotype_resistances",
    )
    variant = m.CharField(max_length=32 * 1024)  # not a FK to Variant

    version = m.IntegerField(
        default=1
    )

    resistance_flag = m.CharField(max_length=10)
