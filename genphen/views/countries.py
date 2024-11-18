from rest_framework import viewsets

from ..models import Country
from ..serializers import CountrySerializer


class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint to manage countries."""

    queryset = Country.objects.all().order_by("country_usual_name")
    serializer_class = CountrySerializer
