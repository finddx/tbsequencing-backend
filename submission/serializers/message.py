from rest_framework import serializers

from submission.models import Message
from identity.serializers import UserNestedSerializer


class MessageSerializer(serializers.ModelSerializer):
    """Message serializer."""

    sender = UserNestedSerializer(read_only=True)

    class Meta:
        """Meta class."""

        model = Message
        fields = (
            "pk",
            "sender",
            "timestamp",
            "content",
        )
        read_only_fields = (
            "pk",
            "sender",
            "timestamp",
        )
