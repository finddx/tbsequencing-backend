from django.db import models as m


class EpidemCutoffValue(m.Model):
    """Epidemiological cut off values model."""

    objects: m.Manager

    drug = m.ForeignKey("Drug", on_delete=m.CASCADE)
    medium_name = m.CharField(max_length=8_192)
    value = m.FloatField()
