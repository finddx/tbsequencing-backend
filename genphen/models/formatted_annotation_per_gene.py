from django.db import models as m


class FormattedAnnotationPerGene(m.Model):
    """Replacing table for genphensql.formatted_annotation_per_gene matview."""

    objects: m.Manager

    variant = m.ForeignKey("Variant", on_delete=m.CASCADE)
    gene_db_crossref = m.ForeignKey("biosql.Dbxref", on_delete=m.DO_NOTHING)
    predicted_effect = m.CharField(max_length=1024)
    nucleotidic_annotation = m.CharField(max_length=1024)
    proteic_annotation = m.CharField(max_length=1024, null=True)
    distance_to_reference = m.IntegerField(null=True)

    # TODO there are some issues getting those unique
    # class Meta:
    #     """FormattedAnnotationPerGene options class."""
    #
    #     constraints = [
    #         m.UniqueConstraint(
    #             fields=["variant_id", "gene_db_crossref_id"],
    #             name="formatted_annotation_per_gene__variant_id__gene_db_crossref_id__uc",
    #         ),
    #     ]
