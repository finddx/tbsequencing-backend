from rest_framework.filters import SearchFilter

from ..models import Gene, GeneSearchHistory


class GeneSearchFilter(SearchFilter):
    """Special filter class for Gene viewset, that updates gene search history."""

    def filter_queryset(self, request, queryset, view):
        """If there are one single search result, update its search counter."""
        queryset = super().filter_queryset(request, queryset, view)

        if queryset.count() == 1:
            self.update_search_counter(queryset[0])
        return queryset

    def update_search_counter(self, gene: Gene):
        """Update search counter for selected Gene."""
        search_history, _ = GeneSearchHistory.objects.get_or_create(
            gene_db_crossref=gene.dbxref,
        )
        search_history.counter += 1
        search_history.save()
