from django.db import models

from .mixin_verdict import VerdictMixin
from .package import Package
from .sequencing_data import SequencingData
from .sequencing_data_hash import SequencingDataHash


class PackageSequencingDataManager(models.Manager):
    """PackageSequencingData manager."""

    def by_prefix(self, prefix: str):
        """Filter records by filename prefix."""
        return self.filter(filename__istartswith=prefix)


class PackageSequencingData(VerdictMixin):
    """
    Package-Sequencing data membership model.

    Includes filename of uploaded file
    """

    objects = PackageSequencingDataManager()

    package = models.ForeignKey(
        Package,
        on_delete=models.CASCADE,
        related_name="assoc_sequencing_datas",
    )
    sequencing_data = models.ForeignKey(
        SequencingData,
        on_delete=models.CASCADE,
        related_name="assoc_packages",
    )

    # in order to distinguish between fastq files
    # related to single sequencing data object
    sequencing_data_hash = models.ForeignKey(
        SequencingDataHash,
        on_delete=models.CASCADE,
        related_name="assoc_packages",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    # uploaded file name (used to match with package samples)
    # we only add sequencing data to a package if it was uploaded
    filename = models.CharField(max_length=1024)

    class Meta:
        """Model options."""

        constraints = [
            models.UniqueConstraint(
                "package",
                "sequencing_data",
                "sequencing_data_hash",
                name="uc__packagesequencingdata__package__sequencing_data__sequencingdatahash",
            ),
        ]
