from rest_framework import serializers

from identity.models import User


class UserNestedSerializer(serializers.HyperlinkedModelSerializer):
    """
    Simpler User model serializer with fewer fields.

    To be included inside other serializers.
    """

    class Meta:
        """Configuration for UserNestedSerializer."""

        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
        ]
