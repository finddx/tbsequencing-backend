from rest_framework import serializers

from ..models import Drug


class DrugReadSerializer(serializers.ModelSerializer):
    """Drug retrieving serializer."""

    code = serializers.CharField(source="drug_code")

    class Meta:
        """Meta class."""

        model = Drug
        fields = (
            "drug_id",
            "drug_name",
            "code",
        )
