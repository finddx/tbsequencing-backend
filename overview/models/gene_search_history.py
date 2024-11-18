from django.db import models


class GeneSearchHistory(models.Model):
    """Genes search history."""

    objects: models.Manager

    gene_db_crossref = models.OneToOneField(
        "biosql.Dbxref",
        on_delete=models.DO_NOTHING,
        related_name="search_history",
        primary_key=True,
    )
    counter = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now=True, auto_created=True)

    class Meta:
        """Meta class."""

        verbose_name_plural = "Gene search histories"

    def __str__(self):
        """Return string representation of a model."""
        return f"Gene Crossref ID={self.gene_db_crossref}  counter={self.counter}"
