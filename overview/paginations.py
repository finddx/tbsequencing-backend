from rest_framework.pagination import PageNumberPagination


class PageSizePageNumberPagination(PageNumberPagination):
    """Pagination class for genetable."""

    page_size = 12
    page_size_query_param = "page_size"
    max_page_size = 1500


class PluggablePageSizePageNumberPagination(PageSizePageNumberPagination):
    """Pluggable pagination."""

    def paginate_queryset(self, queryset, request, view=None):
        """Enable pagination only if "paginated" argument received."""
        if request.GET.get("paginated"):
            return super().paginate_queryset(queryset, request, view)
        return None
