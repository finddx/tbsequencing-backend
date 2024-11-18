from django_filters import rest_framework as filters

from ..models import Drug


class DrugsFilterSet(filters.FilterSet):
    """Drugs filterset."""

    is_associated = filters.BooleanFilter(
        field_name="gene_resistance_associations",
        method="filter_isnull",
    )
    """Filter gene resistance associated drugs."""

    def filter_isnull(self, queryset, name, value):
        """Filter field for isnull."""
        lookup = "__".join([name, "isnull"])
        return queryset.filter(**{lookup: not value}).distinct()

    class Meta:
        """Meta class."""

        model = Drug
        fields = ("is_associated",)
