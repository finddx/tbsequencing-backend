import re

from datetime import date
from typing import Any

from django.contrib.postgres.fields import DateRangeField
from django.db import models as m
from django.utils.html import format_html


class Sample(m.Model):
    """
    Sample model.

    Sample can have multiple aliases in every package.
    Those aliases linked (or not) to mic/pds tests,
    while sample is linked to sequencing data.
    """

    objects: m.Manager

    #
    # original table columns
    #
    # original table have auto-increment sequence for sample_id,
    # but it somehow hasn't attached to the column
    biosample_id = m.IntegerField(null=True, unique=True)
    # sample_name is removed in favor of SampleAlias
    # sra_name is removed in favor of SampleAlias (with origin=SRA)
    submission_date = m.DateField(null=True, default=date.today)
    sampling_date = DateRangeField(null=True, blank=True)
    additional_geographical_information = m.CharField(max_length=8_192, null=True, blank=True)
    latitude = m.CharField(max_length=8_192, null=True, blank=True)
    longitude = m.CharField(max_length=8_192, null=True, blank=True)
    isolation_source = m.CharField(max_length=8_192, null=True, blank=True)


    #For both following choices, we set null =True
    #I.e no data is encoded as null, not as an empty string
    #The possible choices must reflect that.
    class Status(m.TextChoices):
        """Bioanalysis status."""
        UNSET= None
        UNPROCESSED = "Unprocessed"
        PROCESSING = "Processing"
        EXTRACTED = "Extracted"
        FAILED_TO_EXTRACT = "Failed to extract"
        UPLOADED_TO_S3 = "Uploaded to S3"
        FAILED_TO_UPLOAD = "Failed to upload"
        INSERTED = "Inserted"
        ANNOTATED = "Annotated"

    class Origin(m.TextChoices):
        """Origin of sample"""
        UNSET = None
        NCBI = "NCBI"
        TBKB = "TbKb"


    bioanalysis_status = m.CharField(
        max_length=50,
        null=True,
        choices=Status.choices,
        blank=True
    )

    bioanalysis_status_changed_at = m.DateField(null=True)

    country = m.ForeignKey("genphen.Country", m.DO_NOTHING, null=True, blank=True)
    ncbi_taxon = m.ForeignKey("biosql.Taxon", m.DO_NOTHING, to_field="ncbi_taxon_id")

    # package link, to show from which package the sample was created
    package = m.ForeignKey("Package", m.SET_NULL, null=True, related_name="samples")

    # sample can have multiple sequencing data files
    sequencing_data_set: Any  # RelatedManager[SequencingData]
    aliases: Any  # RelatedManager[SampleAlias]

    # genphensql links
    genotypes: Any  # RelatedManager[Genotype]

    # NCBI sync related column.
    origin = m.CharField(
        max_length=128,
        default="TbKb",
        choices=Origin.choices,
        blank=True,
        null=True,
    )

    def get_alias_biosample(self):
        """Aggregate aliases to display in the admin panel"""
        if not self.biosample_id:
            return ""

        biosample_name = (
            self.aliases.filter(origin="BioSample").filter(origin_label="Sample name").first().name
        )

        if biosample_name.startswith("SAMN"):
            address = "https://www.ncbi.nlm.nih.gov/biosample/"
        elif biosample_name.startswith("SAMEA"):
            address = "https://www.ebi.ac.uk/ena/browser/view/"
        elif biosample_name.startswith("SAMD"):
            address = "https://ddbj.nig.ac.jp/resource/biosample/"

        return(
            format_html(
                '<a href="{0}">{1}</a>',
                address + biosample_name,
                biosample_name
            )
        )

    def get_biosample_link(self):
        """Get biosmample link"""
        if not self.biosample_id:
            return ""
        return(format_html(
            '<a href="{0}">{1}</a>',
            "https://www.ncbi.nlm.nih.gov/biosample/"+str(self.biosample_id),
            self.biosample_id
            )
        )


    get_biosample_link.short_description="BioSample ID"

    def get_alias_sequencing_biosample(self):
        """Aggregate aliases to display in the admin panel"""
        return ", ".join(
            {
                x for s in self.aliases.all() for x in s.name.split("__")
                if re.match(r'^[ESD]RS[0-9]+$', x)
            }
        )

    def get_other_aliases(self):
        """Aggregate aliases to display in the admin panel"""
        return ", ".join(
            {
                x for s in self.aliases.all()
                for x in s.name.split("__")
                if not (re.match(r'^SAM(EA|N|D)[0-9]+$', x) or re.match(r'^[ESD]RS[0-9]+$', x))
            }
        )

    def get_scientific_species_name(self):
        """Return the scientific name of the species"""

        return self.ncbi_taxon

#        return TaxonName self.ncbi_taxon.filter(name_class="scientific name").first().name


    get_alias_biosample.short_description = "Primary INSDC alias"
    get_alias_sequencing_biosample.short_description = "Secondary INSDC alias"
    get_other_aliases.short_description = "Other alias(es)"
