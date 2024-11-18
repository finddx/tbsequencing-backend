from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from ..filters import GeneDrugStatsFilter
from ..models.views import GeneDrugStats
from ..paginations import PluggablePageSizePageNumberPagination
from ..serializers import GeneDrugStatsSerializer


class GeneDrugStatsViewSet(
    viewsets.GenericViewSet,
    viewsets.mixins.ListModelMixin,
):
    """Gene drug resistance stats data (table at the bottom of drugs/genes tabs)."""

    queryset = GeneDrugStats.objects.with_stats()
    serializer_class = GeneDrugStatsSerializer
    pagination_class = PluggablePageSizePageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = GeneDrugStatsFilter
