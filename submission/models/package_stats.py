from django.db import models as m
from django.db.models import OuterRef, Exists

from genphen.models import Drug
from .mic_test import MICTest
from .package import Package
from .pds_test import PDSTest


# pylint: disable=too-many-instance-attributes
class PackageStats(m.Model):
    """
    Package statistics, accumulated in a separate table, for performance purposes.

    Stats are updated every time package is changed.
    """

    objects: m.Manager

    package: Package = m.OneToOneField("Package", m.CASCADE, related_name="stats")

    cnt_mic_tests = m.IntegerField(default=0, verbose_name="MIC tests count")
    cnt_pds_tests = m.IntegerField(default=0, verbose_name="PDS tests count")
    cnt_pds_drug_concentration = m.IntegerField(
        default=0,
        verbose_name="PDS drug/concentration combinations count",
    )
    list_mic_drugs = m.JSONField(default=list)
    list_pds_drugs = m.JSONField(default=list)
    cnt_messages = m.IntegerField(default=0, verbose_name="Chat messages count")
    cnt_sample_aliases = m.IntegerField(default=0, verbose_name="Sample aliases count")
    cnt_samples_matched = m.IntegerField(
        default=0,
        verbose_name="Matched samples count",
    )
    cnt_samples_created = m.IntegerField(
        default=0,
        verbose_name="Created samples count",
    )
    cnt_sequencing_data = m.IntegerField(
        default=0,
        verbose_name="Sequencing data files count",
    )

    @property
    def cnt_mic_drugs(self):
        """Return MIC drugs count."""
        return len(self.list_mic_drugs)

    cnt_mic_drugs.fget.short_description = "MIC drugs count"

    @property
    def cnt_pds_drugs(self):
        """Return PDS drugs count."""
        return len(self.list_pds_drugs)

    cnt_pds_drugs.fget.short_description = "PDS drugs count"

    @property
    def list_mic_drug_codes(self):
        """Return MIC drugs as drug preferred code list."""
        return list(
            Drug.objects.filter(drug_id__in=self.list_mic_drugs)
            .order_by("drug_id")
            .values_list("drug_code", flat=True),
        )

    list_mic_drug_codes.fget.short_description = "MIC drugs list"

    @property
    def list_pds_drug_codes(self):
        """Return PDS drugs as drug preferred code list."""
        return list(
            Drug.objects.filter(drug_id__in=self.list_pds_drugs)
            .order_by("drug_id")
            .values_list("drug_code", flat=True),
        )

    list_pds_drug_codes.fget.short_description = "PDS drugs list"

    def update(self):
        """Update package stats."""
        # pylint: disable=no-member
        package: Package = self.package

        self.cnt_mic_tests = package.mic_tests.count()
        self.cnt_pds_tests = package.pds_tests.count()
        self.cnt_messages = package.messages.count()
        self.cnt_sample_aliases = package.sample_aliases.count()
        self.cnt_samples_created = package.samples.count()
        self.cnt_samples_matched = package.sample_aliases.filter(
            sample__isnull=False,
        ).count()
        self.cnt_sequencing_data = package.assoc_sequencing_datas.count()
        self.cnt_pds_drug_concentration = (
            package.pds_tests.values(
                "drug",
                "concentration",
            )
            .distinct()
            .count()
        )

        self.list_mic_drugs = list(
            Drug.objects.filter(
                Exists(
                    MICTest.objects.filter(
                        package=package,
                        drug=OuterRef("drug_id"),
                    ),
                ),
            ).values_list("drug_id", flat=True),
        )
        self.list_pds_drugs = list(
            Drug.objects.filter(
                Exists(
                    PDSTest.objects.filter(
                        package=package,
                        drug=OuterRef("drug_id"),
                    ),
                ),
            ).values_list("drug_id", flat=True),
        )
        self.save()
