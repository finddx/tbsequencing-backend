from django.db import models
from django_pgviews import view


PREFERRED_ANNOTATION_SQL = """
SELECT
    "variant_id",
    "gene_name",
    "predicted_effect",
    "hgvs_value",
    "distance_to_reference" "mii"
FROM genphen_rankedannotation
WHERE rank = 1
"""


class PreferredAnnotation(view.MaterializedView):
    """
    Preferred annotations materialized view.

    Only keep the most relevant variant, DO NOT MERGE if there is a draw.

    Eg,
    A variant overlapping two genes,
        synonymous change in one versus non-synonymous in the second -> only the latter shown.
    A variant overlapping two genes,
        missense in one, stop lost in the second -> draw, both shown.

    This is a simple query, so we store it as a view.
    """

    dependencies = ["genphen.RankedAnnotation"]
    sql = PREFERRED_ANNOTATION_SQL

    objects: models.Manager

    variant_id = models.IntegerField()

    gene_name = models.TextField()
    predicted_effect = models.CharField(max_length=1_024)
    hgvs_value = models.CharField(max_length=1_024)
    mii = models.IntegerField()

    class Meta:
        """Meta class."""

        managed = False
        indexes = [
            models.Index("variant_id", name="preferredannot_variant_id_idx"),
            models.Index("gene_name", name="preferredannot_gene_name_idx"),
        ]
