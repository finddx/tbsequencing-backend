from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import GeneSearchHistory
from ..serializers import GeneSearchSerializer


# TODO make use of pagination and sorting (requires FE work)
class GeneSearchHistoryViewSet(
    viewsets.GenericViewSet,
    viewsets.mixins.ListModelMixin,
):
    """GeneMostSearched views."""

    queryset = GeneSearchHistory.objects.all().order_by("-counter")[:10]
    serializer_class = GeneSearchSerializer

    @action(
        methods=["GET"],
        detail=False,
        url_path="recently",
        url_name="recently",
    )
    def recently_search(self, request, **kwargs):  # pylint: disable=unused-argument
        """List of recently searched genes, ordered by date."""
        queryset = GeneSearchHistory.objects.all().order_by("-date")[:10]
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
