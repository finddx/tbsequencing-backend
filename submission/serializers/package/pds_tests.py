from rest_framework import serializers


class PDSTestsSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    """PDS tests endpoint serializer."""

    file = serializers.FileField(write_only=True, required=False)
