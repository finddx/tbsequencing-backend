from django.db import models
from django_pgviews import view


OVERVIEW_DRUGGENE_SQL = """
SELECT
    gdra.gene_db_crossref_id gene_db_crossref,
    gdra.drug_id drug,
    COALESCE(gene.gene_name, gene.locus_tag) gene_name,
    d.drug_name
FROM genphen_genedrugresistanceassociation gdra
JOIN overview_gene gene on gdra.gene_db_crossref_id = gene.gene_db_crossref
JOIN genphen_drug d ON gdra.drug_id = d.drug_id;
"""


class DrugGene(view.MaterializedView):
    """Drug and gene connected table."""

    sql = OVERVIEW_DRUGGENE_SQL

    objects: models.Manager

    gene_db_crossref = models.IntegerField(unique=True, blank=True, null=True)
    drug = models.IntegerField(unique=True, blank=True, null=True)
    gene_name = models.CharField(max_length=100, unique=False, null=False)
    drug_name = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        """Materialized view should be non-manageable."""

        managed = False
