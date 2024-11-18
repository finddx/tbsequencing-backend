from django.db.models import Max, Q
from django_filters import rest_framework as filters

from .base import NumberInFilter
from ..models.views import GeneDrugStats


class GeneDrugStatsFilter(filters.FilterSet):
    """GeneDrugStats filter."""

    gene_name = filters.CharFilter(field_name="gene_name", lookup_expr="icontains")
    variant_name = filters.CharFilter(
        field_name="variant_name",
        lookup_expr="icontains",
    )
    nucleodic_ann_name = filters.CharFilter(
        field_name="nucleodic_ann_name",
        lookup_expr="icontains",
    )
    proteic_ann_name = filters.CharFilter(
        field_name="proteic_ann_name",
        lookup_expr="icontains",
    )
    consequence = filters.CharFilter(lookup_expr="iexact")
    drug = NumberInFilter(field_name="drug", lookup_expr="in")
    gene_db_crossref_id = NumberInFilter(
        field_name="gene_db_crossref",
        lookup_expr="in",
    )
    variant_grade = filters.CharFilter(lookup_expr="icontains")
    order = filters.OrderingFilter(
        fields=(
            ("resistant_count", "resistantCount"),
            ("susceptible_count", "susceptibleCount"),
            ("intermediate_count", "intermediateCount"),
            ("global_frequency", "globalFrequency"),
            ("total_counts", "totalCounts"),
        ),
    )

    @property
    def qs(self):
        """Apply default filtering by latest variant grade version."""
        parent = super().qs
        if not self.request:
            return parent
        if not self.request.GET.get("variant_grade_version"):
            # if no grade version filter applied,
            # apply default filter - by latest grade version throughout all data
            latest_version = self.queryset.aggregate(
                Max("variant_grade_version"),
            )["variant_grade_version__max"]
            if latest_version is not None:
                # latest version of grade or without grade
                parent = parent.filter(
                    Q(variant_grade_version=latest_version)
                    | Q(variant_grade_version__isnull=True),
                )
        return parent

    class Meta:
        """Meta class."""

        model = GeneDrugStats
        fields = (
            "gene_name",  # pylint: disable=duplicate-code
            "variant_name",
            "nucleodic_ann_name",
            "proteic_ann_name",
            "consequence",
            "drug",
            "gene_db_crossref_id",
            "variant_grade",
            "variant_grade_version",
        )
