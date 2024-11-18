from typing import Any

from django.db import models as m


class SequencingDataHash(m.Model):
    """
    Sequencing data hash model.

    Stores hash of sequencing data file.
    NCBI files should have 2 hashes per file,
    when app-submitted files should have only one per file
    (since app-submitted files should come in pairs).
    """

    class Meta:
        """Sequencing data hash model options."""

        verbose_name_plural = "sequencing data hashes"

        constraints = [
            m.UniqueConstraint(
                "sequencing_data",
                "algorithm",
                "value",
                name="uc__sequencing_data_hash__sequencing_data__algorithm__value",
            ),
        ]

    # changed on_delete to CASCADE,
    # in order to remove any associated hashes when sequencing data object is deleted
    sequencing_data = m.ForeignKey("SequencingData", m.CASCADE, related_name="hashes")
    algorithm = m.CharField(max_length=8_192)  # removed nullable
    value = m.CharField(max_length=8_192)

    # package M2Ms, where the file with such hash featured
    assoc_packages: Any  # RelatedManager[Package]

    def __str__(self):
        """Repr for an object to see in django admin panel."""
        # pylint: disable=no-member
        return f'<SequencingData #{self.sequencing_data_id} hash <{self.algorithm}> "{self.value}">'
