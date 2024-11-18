from django.db import models as m


class TaxonomyStats(m.Model):
    """Taxonomy stats model."""

    objects: m.Manager

    sample = m.ForeignKey("Sample", on_delete=m.CASCADE)
    ncbi_taxon = m.ForeignKey(
        "biosql.Taxon",
        to_field="ncbi_taxon_id",
        on_delete=m.DO_NOTHING,
    )
    value = m.FloatField()

    class Meta:
        """TaxonomyStats model options."""

        constraints = [
            m.UniqueConstraint(
                "sample",
                "ncbi_taxon",
                name="taxonomystats_sample_id_ncbi_taxon_id_uniq",
            ),
        ]
