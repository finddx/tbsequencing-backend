from typing import Any

from django.db import models as m
from django.db.models.functions import Upper
from django.utils.html import format_html

from submission.util.storage import FastqPermanentStorage
from .package import Package
from .sample import Sample


class SequencingData(m.Model):
    """
    Sequencing Data model.

    Stores sequencing data files info, submitted both from the application and NCBI.
    The files themselves stored at S3 bucket.
    """

    objects: m.Manager

    class Meta:
        """Sequencing data model options."""

        verbose_name_plural = "Sequencing data"

        constraints = [
            m.UniqueConstraint(
                "library_name",
                "file_path",
                name="uc__sequencing_data__library_name__file_path",
                # "s3_object",
                # name="uc__sequencing_data__library_name__s3_object",
            ),
        ]
        indexes = [
            # for iexact to work fast
            m.Index(
                Upper("library_name"),
                name="sd__library_name__upper__idx",
            ),
        ]

    class DataLocation(m.TextChoices):
        """Possible data location enum."""

        NCBI = "NCBI"
        TBKB = "TB-Kb"

    class StorageClass(m.TextChoices):
        """Possible S3 storage classes"""

        STANDARD = "STANDARD"
        DEEP_ARCHIVE = "DEEP_ARCHIVE"

    # app-defined column, used to distinguish original file @ matching stage
    created_at = m.DateTimeField(auto_now_add=True)

    # app-defined, filename of file on S3.
    # Defined as FileField
    # in order to get correct download link in admin section
    filename = m.FileField(storage=FastqPermanentStorage(), null=True, blank=True)
    # app-defined, file size in bytes
    file_size = m.BigIntegerField(null=True)

    # library_name could be a Sample name, should be used to match Fastq with Sample
    library_name = m.CharField(max_length=8_192, blank=True)

    # S3 path (without bucket)
    file_path = m.CharField(max_length=8_192, null=True, unique=True)

    # data origin (NCBI, TB-Kb (new), ...)
    data_location = m.CharField(max_length=8_192, choices=DataLocation.choices)

    # Storage class of the file at S3.
    s3_storage_class = m.CharField(
        max_length=50,
        null=True,
        choices=StorageClass.choices,
        default=StorageClass.STANDARD
    )

    # not used by app
    library_preparation_strategy = m.CharField(max_length=8_192, null=True, blank=True)
    dna_source = m.CharField(max_length=8_192, null=True, blank=True)
    dna_selection = m.CharField(max_length=8_192, null=True, blank=True)
    sequencing_platform = m.CharField(max_length=8_192, null=True, blank=True)
    sequencing_machine = m.CharField(max_length=8_192, null=True, blank=True)
    library_layout = m.CharField(max_length=8_192, null=True, blank=True)
    assay = m.CharField(max_length=8_192, null=True, blank=True)

    # FK's
    sample = m.ForeignKey(
        Sample,
        on_delete=m.SET_NULL,  # leave even if sample is deleted
        null=True,  # changed to nullable, so we can link sample later, at matching stage
        related_name="sequencing_data_set",
    )
    # M2M link, in order to track where the object is used
    packages = m.ManyToManyField(
        Package,
        through="PackageSequencingData",
        related_name="sequencing_datas",
    )
    assoc_packages: Any  # RelatedManager[PackageSequencingData]
    hashes: Any  # RelatedManager[SequencingDataHash]

    def __str__(self):
        """Represent instance for admin site."""
        return f'Sequencing data #{self.pk} {self.data_location or ""}'

    def get_filenames(self):
        """Output all filename that were ever associated with this file."""
        return(
            ", ".join(
                [s.filename for s in self.assoc_packages.all()]
            )
        )

    def get_library_url(self):
        """Aggregate aliases to display in the admin panel"""

        if not self.library_name:
            return()
        return(format_html(
            '<a href="{0}">{1}</a>',
            "https://www.ncbi.nlm.nih.gov/sra/"+str(self.library_name),
            self.library_name
            )
        )

    get_library_url.short_description = "Library name"
    get_filenames.short_description = "File name"
