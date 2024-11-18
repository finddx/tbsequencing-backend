from django.db import models as m


class MDRTest(m.Model):
    """Molecular drug resistance tests model."""

    objects: m.Manager

    test_id = m.BigAutoField(primary_key=True)
    test_name = m.CharField(max_length=8_192)
    test_result = m.CharField(max_length=1)

    sample = m.ForeignKey("Sample", m.CASCADE, related_name="mdr_tests")
    drug = m.ForeignKey("genphen.Drug", on_delete=m.CASCADE, related_name="mdr_tests")
