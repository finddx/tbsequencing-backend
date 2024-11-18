from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from ..models import GeneDrugResistanceAssociation
from ..serializers import GeneDrugResistanceAssociationSerializer


class GeneDrugResistanceAssociationsViewSet(
    viewsets.GenericViewSet,
    viewsets.mixins.ListModelMixin,
):
    """Gene drug resistance associations viewset."""

    queryset = (
        GeneDrugResistanceAssociation.objects.select_related("gene_db_crossref__data")
#        .filter(gene_db_crossref__data__gene_name__isnull=False)
        .order_by("tier", "gene_db_crossref")
        .all()
    )
    serializer_class = GeneDrugResistanceAssociationSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ["drug_id", "tier"]
