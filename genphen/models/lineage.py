from django.db import models


class Lineage(models.Model):
    """
    Stores the variant IDs to lineage values.
    The taxonomic level can either be lineage or sublineage.
    This way values can be stored as integer.
    For the variants that are markers of lineage 4 or 4.9 (ie the reference),
    we need to look for the absence of all complementary variants.
    For instance, at 498531 A is marker for 4 so it is the reference allele.
    So we count only if all 498531 C,G,T are absent.
    """

    objects: models.Manager

    lineage_numbering = models.CharField(
        max_length=20
    )

    lineage_name = models.CharField(
        max_length=40
    )
