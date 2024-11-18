from django.db import models as m

from genphen.models import Drug, GrowthMedium, PDSAssessmentMethod
from .package import Package
from .sample import Sample
from .sample_alias import SampleAlias


class PDSTest(m.Model):
    """Phenotypic drug susceptibility tests non-managed model."""

    objects: m.Manager

    class Meta:
        """PDSTest model options."""

        verbose_name_plural = "PDS Tests"

    class TestResult(m.Choices):
        """Test result symbols."""

        S = "S"
        R = "R"
        I = "I"

    concentration = m.FloatField(blank=True, null=True)
    test_result = m.CharField(max_length=1, choices=TestResult.choices, null=True)
    staging = m.BooleanField(default=True)

    # Relations
    # remove all tests on alias remove
    sample_alias = m.ForeignKey(SampleAlias, m.CASCADE, related_name="pds_tests")
    # keep tests on sample remove
    sample = m.ForeignKey(Sample, m.SET_NULL, null=True, related_name="pds_tests")
    """Surplus sample link, repeats sample_alias.sample."""
    # restrict cascade deletion
    drug = m.ForeignKey(Drug, m.DO_NOTHING, null=True, related_name="pds_tests")
    # restrict cascade deletion
    medium = m.ForeignKey(
        GrowthMedium,
        m.DO_NOTHING,
        null=True,
        related_name="pds_tests",
    )
    # restrict cascade deletion
    method = m.ForeignKey(
        PDSAssessmentMethod,
        m.DO_NOTHING,
        null=True,
        related_name="pds_tests",
    )
    # remove all tests on package remove
    package = m.ForeignKey(Package, m.CASCADE, related_name="pds_tests")
