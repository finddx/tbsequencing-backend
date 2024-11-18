from django.db import models as m


class SmearMicroscopyResult(m.Model):
    """Smear microscopy results model."""

    objects: m.Manager

    test_id = m.BigAutoField(primary_key=True)
    sample = m.ForeignKey("Sample", on_delete=m.CASCADE)
    smear_result = m.CharField(max_length=8_192)
