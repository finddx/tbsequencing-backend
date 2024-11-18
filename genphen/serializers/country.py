from rest_framework import serializers

from genphen.models import Country


class CountrySerializer(serializers.ModelSerializer):
    """Country model serializer for REST API."""

    class Meta:
        """Configuration for CountrySerializer."""

        model = Country
        fields = [
            "country_id",
            "two_letters_code",
            "three_letters_code",
            "country_usual_name",
            "country_official_name",
        ]
