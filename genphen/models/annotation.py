from django.db import models as m


class Annotation(m.Model):
    """Annotations model."""

    objects: m.Manager

    annotation_id = m.BigAutoField(primary_key=True)
    reference_db_crossref = m.ForeignKey("biosql.Dbxref", on_delete=m.DO_NOTHING)
    hgvs_value = m.CharField(max_length=8_192, db_index=True)
    predicted_effect = m.CharField(max_length=8_192)
    distance_to_reference = m.IntegerField(null=True)

    variants = m.ManyToManyField(
        "Variant",
        through="VariantToAnnotation",
        related_name="annotations",
    )

    class Meta:
        """Annotation model options."""

        constraints = [
            m.UniqueConstraint(
                "reference_db_crossref",
                "hgvs_value",
                "predicted_effect",
                name="annotation_dbxref_hgvs_value_predicted_effect_uniq",
            ),
        ]
