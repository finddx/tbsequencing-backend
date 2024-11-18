from django.db import models
from django_pgviews import view


LOCUS_TAG_SQL = """
SELECT
    sdb.dbxref_id "gene_db_crossref_id",
    sqv.value "locus_tag_name"
FROM biosql.seqfeature_dbxref sdb
     INNER JOIN biosql.seqfeature_qualifier_value sqv ON sqv.seqfeature_id = sdb.seqfeature_id
     INNER JOIN biosql.seqfeature ON sqv.seqfeature_id = seqfeature.seqfeature_id
     INNER JOIN biosql.term ON (term.term_id = sqv.term_id AND term.name = 'locus_tag')
     INNER JOIN biosql.term t2 ON (t2.term_id = seqfeature.type_term_id AND t2.name = 'gene')
"""


class LocusTag(view.View):
    """
    Locus tag view model.

    This view links GeneID dbxref id to Locus Tag.
    """

    dependencies = []
    sql = LOCUS_TAG_SQL

    objects: models.Manager

    gene_db_crossref_id = models.IntegerField()
    locus_tag_name = models.TextField()

    class Meta:
        """Meta class."""

        managed = False
