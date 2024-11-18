from django.db import models as m


class Genotype(m.Model):
    """Genotype model."""

    objects: m.Manager

    genotype_id = m.BigAutoField(primary_key=True)

    # 3 fields below are unique together
    sample = m.ForeignKey("Sample", on_delete=m.CASCADE)
    variant = m.ForeignKey("genphen.Variant", on_delete=m.CASCADE)
    genotyper = m.CharField(max_length=128)

    quality = m.FloatField()
    reference_ad = m.IntegerField()
    alternative_ad = m.IntegerField()
    total_dp = m.IntegerField()
    genotype_value = m.CharField(max_length=128)

    class Meta:
        """Model settings class."""

        constraints = [
            m.UniqueConstraint(
                "sample",
                "variant",
                "genotyper",
                name="genotype_sample_id_variant_id_genotyper__key",
            ),
        ]
