from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from ..filters import ResistanceStatsFilter
from ..models import SampleDrugResultStats
from ..serializers import (
    ResistanceStatsByDrugSerializer,
    ResistanceStatsByCountrySerializer,
)


class ResistanceStatsByDrugViewSet(
    viewsets.GenericViewSet,
    viewsets.mixins.ListModelMixin,
):
    """Resistance stats by drug (drug tab graph)."""

    filter_backends = (DjangoFilterBackend,)
    filterset_class = ResistanceStatsFilter
    serializer_class = ResistanceStatsByDrugSerializer

    def get_queryset(self):
        """Return queryset."""
        return SampleDrugResultStats.objects.by_drug()


class ResistanceStatsByCountryViewSet(
    viewsets.GenericViewSet,
    viewsets.mixins.ListModelMixin,
):
    """Resistance stats by country (overview tab graph)."""

    filter_backends = (DjangoFilterBackend,)
    filterset_class = ResistanceStatsFilter
    serializer_class = ResistanceStatsByCountrySerializer

    def get_queryset(self):
        """Return queryset."""
        return SampleDrugResultStats.objects.by_country()
