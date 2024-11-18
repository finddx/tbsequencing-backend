# from datetime import date

from django_filters import rest_framework as filters
# from psycopg2.extras import DateRange

from ..models import SampleDrugResultStats


class ResistanceStatsFilter(filters.FilterSet):
    """Resistance stats filter."""

    # year_gte filters inside .qs
    # year_lte filters inside .qs
    # country_id filters inside .qs

    class Meta:
        """Meta class."""

        model = SampleDrugResultStats
        fields = (
            "drug",
            "resistance_type",
        )

    @property
    def qs(self):
        """
        Apply custom filtering.

        - sampling_date DateRange filter, based on legacy year_lte/year_gte filters;
        - country filter, supporting list of countries, without validation.
        """
        parent = super().qs
        if not self.request:
            return parent

        # filter by countries list
        country = self.request.GET.getlist("country_id")
        if country:
            parent = parent.filter(country__in=country)

        return parent
        # year_gte = self.request.GET.get("year_gte")
        # year_lte = self.request.GET.get("year_lte")
        # if not year_lte and not year_gte:
        #     return parent

        # # if None, bound will be treated as infinite
        # year_gte = date(int(year_gte), 1, 1) if year_gte else None
        # year_lte = date(int(year_lte), 12, 31) if year_lte else None

        # custom "overlaps" lookup expression can be found in overview.lookups module
        # return parent.filter(sampling_date__overlaps=DateRange(year_gte, year_lte))
