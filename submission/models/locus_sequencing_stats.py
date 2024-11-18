from django.db import models as m


class LocusSequencingStats(m.Model):
    """Locus sequencing stats model."""

    objects: m.Manager

    sample = m.ForeignKey("Sample", on_delete=m.CASCADE)
    gene_db_crossref = m.ForeignKey("biosql.Dbxref", on_delete=m.DO_NOTHING)
    mean_depth = m.FloatField()
    coverage_10x = m.FloatField()
    coverage_15x = m.FloatField()
    coverage_20x = m.FloatField()
    coverage_30x = m.FloatField()

    class Meta:
        """LocusSequencingStats options."""

        constraints = [
            m.UniqueConstraint(
                "sample",
                "gene_db_crossref",
                name="locusseq_sample_dbxref_key",
            ),
        ]
