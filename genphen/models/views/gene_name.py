from django.db import models
from django_pgviews import view


GENE_NAME_SQL = """
SELECT
    sdb.dbxref_id "gene_db_crossref_id",
    sqv.value "gene_name"
FROM biosql.seqfeature_dbxref sdb
     INNER JOIN biosql.seqfeature_qualifier_value sqv ON sqv.seqfeature_id = sdb.seqfeature_id
     INNER JOIN biosql.seqfeature ON sqv.seqfeature_id = seqfeature.seqfeature_id
     INNER JOIN biosql.term ON (term.term_id = sqv.term_id AND term.name = 'gene')
     INNER JOIN biosql.term t2 ON (t2.term_id = seqfeature.type_term_id AND t2.name = 'gene')
"""


class GeneName(view.View):
    """
    Gene name view model.

    This view links GeneID dbxref id to gene name if it exists.
    """

    dependencies = []
    sql = GENE_NAME_SQL

    objects: models.Manager

    gene_db_crossref_id = models.IntegerField()
    gene_name = models.TextField()

    class Meta:
        """Meta class."""

        managed = False
