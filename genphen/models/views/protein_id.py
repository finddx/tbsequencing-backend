from django.db import models
from django_pgviews import view


PROTEIN_ID_SQL = """
SELECT
    dbxref.dbxref_id "protein_db_crossref_id",
    sdb.dbxref_id "gene_db_crossref_id"
FROM biosql.dbxref
         INNER JOIN biosql.seqfeature_qualifier_value sqv ON sqv.value = dbxref.accession
         INNER JOIN biosql.seqfeature_dbxref sdb ON (sdb.seqfeature_id = sqv.seqfeature_id)
WHERE dbname = 'Protein'
"""


class ProteinId(view.View):
    """
    Protein ID view model.

    This view links the GeneID dbxref id to Protein dbxref id.
    """

    dependencies = []
    sql = PROTEIN_ID_SQL

    objects: models.Manager

    protein_db_crossref_id = models.IntegerField()
    gene_db_crossref_id = models.IntegerField()

    class Meta:
        """Meta class."""

        managed = False
