from rest_framework import serializers
from django.core.validators import MaxValueValidator, MinValueValidator


class ResistanceStatsDataSerializer(serializers.Serializer):  # pylint: disable=W0223
    """Read global drug serializer."""

    susceptible = serializers.IntegerField()
    resistant = serializers.IntegerField()
    intermediate = serializers.IntegerField()
    ratio_susceptible = serializers.DecimalField(
        max_digits=4,
        decimal_places=1,
        validators=[
            MaxValueValidator(100),
            MinValueValidator(0)
        ]
    )
    ratio_resistant = serializers.DecimalField(
        max_digits=4,
        decimal_places=1,
        validators=[
            MaxValueValidator(100),
            MinValueValidator(0)
        ]
    )
    ratio_intermediate = serializers.DecimalField(
        max_digits=4,
        decimal_places=1,
        validators=[
            MaxValueValidator(100),
            MinValueValidator(0)
        ]
    )

    total = serializers.IntegerField()


class ResistanceStatsByDrugSerializer(
    ResistanceStatsDataSerializer,
):  # pylint: disable=abstract-method
    """Resistance stats by drug serializer."""

    drug = serializers.IntegerField()


class ResistanceStatsByCountrySerializer(
    ResistanceStatsDataSerializer,
):  # pylint: disable=abstract-method
    """Resistance stats by country serializer."""

    country_id = serializers.CharField(source="country")
