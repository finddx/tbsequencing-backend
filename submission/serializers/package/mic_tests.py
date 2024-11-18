from rest_framework import serializers


class MICTestsSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    """MIC tests endpoint serializer."""

    file = serializers.FileField(write_only=True, required=False)
