from django.db import models
from django_pgviews import view


RANKED_ANNOTATION_SQL = """
SELECT
  vta.variant_id,
  annotation_id,
  x.gene_name,
  annotation.predicted_effect,
  annotation.hgvs_value,
  annotation.distance_to_reference,
  RANK() OVER(
    PARTITION BY variant_id ORDER BY CASE
     WHEN
        ((predicted_effect != 'synonymous_variant' AND protein_id.protein_db_crossref_id IS NOT NULL)
            OR
        (predicted_effect = 'non_coding_transcript_exon_variant'))
        THEN 1
     WHEN (predicted_effect = 'synonymous_variant' AND locustag1.locus_tag_name IS NOT NULL)
        THEN 2
     WHEN predicted_effect IN ('upstream_gene_variant', 'downstream_gene_variant')
        THEN distance_to_reference + 2
     END
  ) AS rank
FROM genphen_varianttoannotation vta
NATURAL JOIN genphen_annotation annotation
LEFT JOIN genphen_locustag locustag1
    ON locustag1.gene_db_crossref_id = annotation.reference_db_crossref_id
LEFT JOIN genphen_proteinid protein_id
    ON protein_id.protein_db_crossref_id = annotation.reference_db_crossref_id
INNER JOIN (
    SELECT
        locustag2.gene_db_crossref_id,
        COALESCE(gene_name.gene_name, locustag2.locus_tag_name) gene_name
    FROM genphen_locustag locustag2
    LEFT JOIN genphen_genename gene_name
        ON gene_name.gene_db_crossref_id = locustag2.gene_db_crossref_id
  ) x
    ON x.gene_db_crossref_id = COALESCE(protein_id.gene_db_crossref_id, locustag1.gene_db_crossref_id
)
"""


class RankedAnnotation(view.MaterializedView):
    """
    Ranked annotations materialized view.

    This view ranks the most relevant annotation per variant.
    Prioritization:
        1. Non-synonymous OR non coding variant;
        2. Synonymous variant;
        3. Upstream/Downstream variant ordered by distance.
    """

    dependencies = ["genphen.GeneName", "genphen.LocusTag", "genphen.ProteinId"]
    sql = RANKED_ANNOTATION_SQL

    objects: models.Manager

    variant_id = models.IntegerField()
    annotation_id = models.BigIntegerField()

    gene_name = models.TextField()
    predicted_effect = models.CharField(max_length=1_024)
    hgvs_value = models.CharField(max_length=1_024)
    distance_to_reference = models.IntegerField()
    rank = models.BigIntegerField()

    class Meta:
        """Meta class."""

        managed = False
        indexes = [
            models.Index("variant_id", name="rankedannot_variant_id_idx"),
            models.Index("annotation_id", name="rankedannot_annotation_id_idx"),
            models.Index("gene_name", name="rankedannot_gene_name_idx"),
        ]
