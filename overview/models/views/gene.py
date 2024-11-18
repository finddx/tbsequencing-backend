from django.db import models
from django_pgviews import view


OVERVIEW_GENE_SQL = """
WITH terms_ranked AS (
    SELECT
        sd.dbxref_id,
        term.name,
        sqv.value,
        ROW_NUMBER() OVER (PARTITION BY sqv.value ORDER BY sqv.seqfeature_id DESC) AS rank
        FROM biosql.seqfeature_qualifier_value sqv
        INNER JOIN biosql.seqfeature_dbxref sd on sd.seqfeature_id = sqv.seqfeature_id
        INNER JOIN biosql.term ON sqv.term_id=term.term_id
),
terms AS (
    -- 1<->1 dbxref <-> {term name + term value}
    SELECT
        dbxref_id,
        name,
        value
    FROM terms_ranked
    WHERE rank = 1
),
ranked_locations AS (
    SELECT
        sd.dbxref_id,
        l.start_pos,
        l.end_pos,
        l.strand,
        ROW_NUMBER() OVER (PARTITION BY sd.dbxref_id ORDER BY sd.seqfeature_id DESC) AS rank
    FROM biosql.seqfeature_dbxref sd
    JOIN biosql.location l ON sd.seqfeature_id = l.seqfeature_id
),
locations AS (
    -- 1<->1 dbxref <-> biosql.location (latest by seqfeature_id)
    SELECT
        dbxref_id,
        start_pos,
        end_pos,
        strand
    FROM ranked_locations
    WHERE rank = 1
)

SELECT
    d.accession AS ncbi_id,
    d.dbxref_id AS gene_db_crossref,  -- legacy dbxref_id copy
    d.dbxref_id,
    l.start_pos,
    l.end_pos,
    l.strand,
    gene_name.value gene_name,
    locus_tag.value locus_tag,
    gene_description.value gene_description,
    gene_type.value gene_type,
    length(protein_sequence.value) protein_length
FROM biosql.dbxref d
JOIN locations l ON d.dbxref_id = l.dbxref_id
LEFT JOIN terms gene_name
    ON gene_name.dbxref_id = d.dbxref_id and gene_name.name = 'gene'
LEFT JOIN terms locus_tag
    ON locus_tag.dbxref_id = d.dbxref_id and locus_tag.name = 'locus_tag'
LEFT JOIN terms gene_description
    ON gene_description.dbxref_id = d.dbxref_id and gene_description.name = 'product'
LEFT JOIN terms gene_type
    ON gene_type.dbxref_id = d.dbxref_id and gene_type.name = 'protein_id'
LEFT JOIN terms protein_sequence
    ON protein_sequence.dbxref_id = d.dbxref_id and protein_sequence.name = 'translation'
WHERE d.dbname::text = 'GeneID'::text
"""


class Gene(view.MaterializedView):
    """
    Genes materialized view.

    Constructed from biosql data.
    """

    sql = OVERVIEW_GENE_SQL

    objects: models.Manager

    dbxref = models.OneToOneField(
        "biosql.Dbxref",
        models.DO_NOTHING,
        related_name="data",
        primary_key=True,
    )

    # backwards-compatibility dbxref field
    gene_db_crossref = models.IntegerField(null=True)
    ncbi_id = models.CharField(max_length=128, null=True)
    start_pos = models.IntegerField(null=True)
    end_pos = models.IntegerField(null=True)
    strand = models.IntegerField(null=True)
    gene_name = models.TextField(null=True)
    locus_tag = models.TextField(null=True)
    gene_description = models.TextField(null=True)
    gene_type = models.TextField(null=True)
    protein_length = models.IntegerField(null=True)

    class Meta:
        """Meta class."""

        managed = False

    def __str__(self):
        """Return string representation of a model."""
        return f"Gene {self.gene_name}"
