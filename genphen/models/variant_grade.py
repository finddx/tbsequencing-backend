from django.db import models as m


class VariantGrade(m.Model):
    """Variant grades model."""

    objects: m.Manager


    position = m.IntegerField(
        null=True
    )

    alternative_nucleotide = m.CharField(
        null=True,
        max_length=200
    )

    reference_nucleotide = m.CharField(
        null=True,
        max_length=200
    )

    variant = m.ForeignKey(
        "Variant",
        on_delete=m.CASCADE,
        related_name="grades",
        null=True,
    )

    drug = m.ForeignKey("Drug", on_delete=m.CASCADE, related_name="variant_grades")
    grade = m.IntegerField()
    grade_version = m.IntegerField()

    class Meta:
        """VariantGrade model options."""

        constraints = [
            m.UniqueConstraint(
                "variant",
                "drug",
                "grade_version",
                name="variantgrade_variant_drug_grade_version_key",
            ),
        ]
