from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..filters import GeneSearchFilter
from ..models import Gene
from ..paginations import PageSizePageNumberPagination
from ..serializers import GeneSerializer, GeneRetrieveSerializer


class GeneViewSet(
    viewsets.GenericViewSet,
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.RetrieveModelMixin,
):
    """Genes viewset."""

    pagination_class = PageSizePageNumberPagination
    queryset = (
        Gene.objects.all()
        .select_related("dbxref")
        .prefetch_related("dbxref__drug_resistance_associations")
        .order_by("dbxref")
    )

    filter_backends = (GeneSearchFilter,)
    search_fields = ["gene_name", "locus_tag", "ncbi_id"]

    def get_serializer_class(self):
        """
        Use custom serializer for single gene retrieve.

        Legacy behaviour (we don't need custom serializer),
            but changing it requires heavy frontend work to be refactored.
        """
        if self.action == "retrieve":
            return GeneRetrieveSerializer
        return GeneSerializer

    @action(
        methods=["GET"],
        detail=False,
        url_path="genome-context",
        url_name="genomecontext",
    )
    def genome_context(self, request, **kwargs):  # pylint: disable=unused-argument
        """List of genes by locations."""
        start_pos = request.GET.get("start_pos", None)
        end_pos = request.GET.get("end_pos", None)
        if not start_pos or not end_pos:
            result = {
                "detail": "Please add genome positions.",
            }
            return Response(result)
        queryset = Gene.objects.filter(
            Q(start_pos__lte=end_pos, end_pos__gte=end_pos)
            | Q(end_pos__gte=start_pos, start_pos__lte=start_pos)
            | Q(start_pos__gte=start_pos, end_pos__lte=end_pos),
        ).order_by("start_pos")
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
