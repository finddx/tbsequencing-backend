from django.db import models

class PromoterDistance(models.Model):
    """Genes that are associated with drugs."""

    objects: models.Manager

    gene_db_crossref = models.ForeignKey(
        "biosql.Dbxref",
        on_delete=models.DO_NOTHING,
        related_name="promoter_locations",
    )

    start = models.IntegerField(
    )

    end = models.IntegerField(
    )
