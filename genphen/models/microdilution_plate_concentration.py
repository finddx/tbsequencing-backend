from django.db import models as m

from .drug import Drug


class MicrodilutionPlateConcentration(m.Model):
    """Microdilution plate concentration model."""

    objects: m.Manager

    plate = m.CharField(max_length=8_192)
    drug = m.ForeignKey(Drug, on_delete=m.CASCADE)
    concentration = m.FloatField()

    class Meta:
        """Model options."""

        constraints = [
            m.UniqueConstraint(
                "plate",
                "drug",
                "concentration",
                name="microdil_plate_drug_con_key",
            ),
        ]
