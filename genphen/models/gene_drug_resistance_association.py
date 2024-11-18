from django.db import models

from .drug import Drug


class GeneDrugResistanceAssociation(models.Model):
    """Genes that are associated with drugs."""

    objects: models.Manager

    gene_db_crossref = models.ForeignKey(
        "biosql.Dbxref",
        on_delete=models.DO_NOTHING,
        related_name="drug_resistance_associations",
    )

    drug = models.ForeignKey(
        Drug,
        on_delete=models.CASCADE,
        related_name="gene_resistance_associations",
    )

    tier = models.IntegerField()
