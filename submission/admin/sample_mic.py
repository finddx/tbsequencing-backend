from submission.models import MICTest

from .sample_pdst import PhenotypicDrugSusceptibilityTestInline

class MinimumInhibitoryConcentrationValueInline(PhenotypicDrugSusceptibilityTestInline):
    """Package sequencing data inline widget."""

    model = MICTest
    readonly_fields = [
        "get_drug",
        "plate",
        "range",
        "package",
    ]

    fields = [
        "get_drug",
        "plate",
        "range",
        "package",
    ]

    verbose_name_plural = "MIC"
    verbose_name = "Minimum inhibitory concentration value"
