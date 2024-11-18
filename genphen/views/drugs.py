from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from ..filters import DrugsFilterSet
from ..models import Drug
from ..serializers import DrugReadSerializer


class DrugViewSet(
    viewsets.GenericViewSet,
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.RetrieveModelMixin,
):
    """Drug views."""

    queryset = Drug.objects.all().order_by("drug_name")  # default ordering
    serializer_class = DrugReadSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = DrugsFilterSet
