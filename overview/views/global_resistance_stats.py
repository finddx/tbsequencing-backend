from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import GlobalResistanceStats


class GlobalResistanceStatsView(APIView):
    """Global resistance statistics for samples."""

    permission_classes = []

    def get(
        self,
        request,
        format=None,
    ):  # pylint: disable=redefined-builtin,unused-argument
        """Return single record with global resistance statistics numbers."""
        record = GlobalResistanceStats.objects.with_ratios().all()[0]
        data = {
            "countries": [],
            "total": {
                "totalSum": record["total_samples"],
                "monoResSum": record["mono_resistant"],
                "polyResSum": record["poly_resistant"],
                "multiDrugResSum": record["multidrug_resistant"],
                "extDrugResSum": record["extensive_drug_resistant"],
                "rifResSum": record["rifampicin_resistant"],
                "ratioMonoRes": record["ratio_mono_res"],
                "ratioPolyRes": record["ratio_poly_res"],
                "ratioMultiDrugRes": record["ratio_multi_drug_res"],
                "ratioExtDrugRes": record["ratio_ext_drug_res"],
                "ratioRifRes": record["ratio_rif_res"],
            },
        }
        return Response(data)
