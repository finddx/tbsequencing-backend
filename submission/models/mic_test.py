from django.contrib.postgres.fields import DecimalRangeField
from django.db import models as m

from genphen.models import Drug
from .package import Package
from .sample import Sample
from .sample_alias import SampleAlias


class MICTest(m.Model):
    """Minimum inhibitory concentration test model."""

    objects: m.Manager

    plate = m.CharField(max_length=8_192)
    range = DecimalRangeField(null=True)
    staging = m.BooleanField(default=True)

    # remove tests on alias remove
    sample_alias = m.ForeignKey(SampleAlias, m.CASCADE, related_name="mic_tests")
    # keep tests on sample remove
    sample = m.ForeignKey(Sample, m.SET_NULL, null=True, related_name="mic_tests")
    """Repeats sample_alias.sample"""

    # restrict cascade deletion
    drug = m.ForeignKey(Drug, on_delete=m.DO_NOTHING, related_name="mic_tests")
    # remove all tests on package remove
    package = m.ForeignKey(Package, on_delete=m.CASCADE, related_name="mic_tests")
