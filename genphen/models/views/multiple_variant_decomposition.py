from django.db import models
from django_pgviews import view


MULTIPLE_VARIANT_DECOMPOSITION_SQL = """
SELECT
    z."variant_id" "mnv_variant_id",
    v2."variant_id" "single_variant_id"
FROM (
  SELECT
      "variant_id",
      "position",
      regexp_split_to_table("reference_nucleotide", '(?=([ATCG])+)') "ref",
      regexp_split_to_table(alternative_nucleotide, '(?=([ATCG])+)') "alt",
      generate_series(0, length("reference_nucleotide")-1) "shift"
  FROM "genphen_variant"
  WHERE length("reference_nucleotide")>1
    AND length("reference_nucleotide")=length("alternative_nucleotide")
)  z
LEFT JOIN "genphen_variant" "v2" ON (
    v2.reference_nucleotide=ref
        and v2.alternative_nucleotide=alt
        and v2.position=(z.position+z."shift")
    )
WHERE "ref"!="alt"
"""


class MultipleVariantDecomposition(view.MaterializedView):
    """
    Multiple variant decomposition materialized view.

    Decomposition between "multiple nucleotide variants"
        and their individual single nucleotide variants.
    This view is necessary when performing the variant extraction
        for frequency purposes for instance.
    """

    dependencies = []
    sql = MULTIPLE_VARIANT_DECOMPOSITION_SQL

    objects: models.Manager

    mnv_variant_id = models.IntegerField()
    single_variant_id = models.IntegerField()

    class Meta:
        """Meta class."""

        managed = False
