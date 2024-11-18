from typing import Any

from django.contrib.postgres.fields import DateRangeField
from django.db import models
from django.db.models.functions import Upper

from .mixin_verdict import VerdictMixin


class SampleAlias(VerdictMixin):
    """
    Sample aliases model.

    Sample aliases are imported along with MIC/PDS tests,
    and later can be associated with samples at matching stage.
    """

    objects = models.Manager()

    class MatchSource(models.TextChoices):
        """How exactly the alias was matched."""

        NO_MATCH = "NO_MATCH", "No match found"
        """Alias was not matched."""

        FASTQ_UPLOADED = "FASTQ_UPLOADED", "Uploaded FASTQ file"
        """Alias matched through uploaded FASTQ file by filename prefix."""

        FASTQ_UPLOADED_NEW_SAMPLE = (
            "FASTQ_UPLOADED_NEW_SAMPLE",
            "Uploaded FASTQ file, new sample",
        )
        """Alias matched through uploaded FASTQ file by filename prefix, new sample created."""

        FASTQ_EXISTING = "FASTQ_EXISTING", "Existing FASTQ file"
        """Alias matched by name with existing FASTQ file by its library_name."""

        NCBI = "NCBI", "NCBI sample name"
        """Alias matched by name with NCBI data."""

        NCBI_FASTQ = "NCBI_FASTQ", "Existing FASTQ file at NCBI"
        """Alias matched by uploaded FASTQ file MD5 with NCBI accession keys."""

        USER_ALIAS = "USER_ALIAS", "Existing user alias"
        """Alias matched by name with user alias, uploaded earlier."""

    class Origin(models.TextChoices):
        """Enum for sample alias origins."""

        SRS = "SRS"  # comes from pipeline
        BIOSAMPLE = "BioSample"  # comes from pipeline
        TBKB = "TBKB"  # comes from webapp

    # Columns
    name = models.CharField(max_length=2048)
    created_at = models.DateTimeField(auto_now_add=True)
    fastq_prefix = models.CharField(max_length=2048, null=True)
    """
    Used to match sample with sequencing data by uploaded fastq filename.
    The prefix is optional and unique within package.
    """

    match_source = models.CharField(
        max_length=64,
        choices=MatchSource.choices,
        null=True,
    )
    """How exactly the alias was matched with sample."""

    # Relations
    # we drop aliases together with package (samples stay)
    package = models.ForeignKey(
        "Package",
        on_delete=models.CASCADE,
        related_name="sample_aliases",
    )
    # we disconnect aliases from sample when it is dropped
    sample = models.ForeignKey(
        "Sample",
        null=True,
        on_delete=models.SET_NULL,
        related_name="aliases",
    )
    """Can be created without sample association, and associated later at matching stage."""

    # Additional data, merged into sample when matched (the data comes from PDS tests)
    country = models.ForeignKey("genphen.Country", models.SET_NULL, null=True)
    sampling_date = DateRangeField(null=True)

    # NCBI sync related fields.
    # origin tells us the source of the alias, such as SRA/NCBI/etc.
    # origin_label serves as freeform description for origin.
    origin = models.CharField(
        max_length=128,
        choices=Origin.choices,
        default=Origin.TBKB,  # that default is only for django
    )
    origin_label = models.CharField(max_length=1024, default="")

    # Backrefs
    mic_tests: Any  # RelatedManager[MICTest]
    pds_tests: Any  # RelatedManager[PDSTest]

    class Meta:
        """Model options."""

        verbose_name_plural = "sample aliases"

        indexes = [
            # for iexact to work fast
            models.Index(Upper("name"), name="samplealias__name__upper__idx"),
        ]
        constraints = [
            # Sample alias name should be unique within submission package.
            models.UniqueConstraint(
                "package",
                "name",
                name="uc__samplealias__package__name",
            ),
            # Fastq prefix should be unique within submission package.
            # It can be null, but never duplicated.
            # To associate sample alias with multiple FASTQs,
            # we upload multiple fastqs with same prefix.
            models.UniqueConstraint(
                "package",
                "fastq_prefix",
                name="uc__samplealias__package__fastq_prefix",
            ),
        ]
