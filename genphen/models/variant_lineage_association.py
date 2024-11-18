from django.db import models


class VariantLineageAssociation(models.Model):
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

    variant = models.ForeignKey(
        "genphen.Variant",
        on_delete=models.CASCADE,
        related_name="lineage_marker",
        null=True,
    )

    position = models.IntegerField(
        null=True
    )

    alternative_nucleotide = models.CharField(
        null=True,
        max_length=1
    )

    # This attribute is needed because for the markers for lineage 4 and sublineage 4.9
    # We need to verify the absence of certain genotypes, instead of their presence
    count_presence = models.BooleanField(
        default=True
    )

    lineage = models.ForeignKey(
        "genphen.Lineage",
        on_delete=models.CASCADE,
        related_name="marker"
    )
