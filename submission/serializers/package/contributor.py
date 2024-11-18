from rest_framework_nested.serializers import NestedHyperlinkedModelSerializer
from rest_framework import serializers
from submission.models import Contributor


class NestedContributorSerializer(NestedHyperlinkedModelSerializer):
    """Contributor model serializer, that is used in package nested view."""

    parent_lookup_kwargs = {
        "package_pk": "package__pk",
    }

    class Meta:
        """Options for serializer."""

        model = Contributor
        extra_kwargs = {
            "url": {"view_name": "submission:contributor-detail"},
        }
        fields = [
            "pk",
            "url",
            "first_name",
            "last_name",
            "role",
        ]
        read_only_fields = [
            "pk",
            "url",
        ]


class CreateContributorsSerializer(
    serializers.Serializer,
):  # pylint: disable=abstract-method
    """Special serializer for bulk creation of contributors."""

    contributors = NestedContributorSerializer(many=True)

    def create(self, validated_data):
        """Create bulk contributors."""
        objects = []
        for item in self.validated_data["contributors"]:
            obj = Contributor.objects.create(**item)
            objects.append(obj)
        return {"contributors": objects}

    class Meta:
        """Options class."""

        fields = [
            "contributors",
        ]
