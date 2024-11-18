from rest_framework import serializers
from rest_framework_nested.serializers import NestedHyperlinkedModelSerializer
from django.db import IntegrityError
from submission.models import SampleAlias


class NestedSampleAliasSerializer(NestedHyperlinkedModelSerializer):
    """Sample alias model serializer, that is used in package nested view."""

    parent_lookup_kwargs = {
        "package_pk": "package__pk",
    }

    # annotated in viewset's queryset
    mic_tests_count = serializers.IntegerField(read_only=True)
    pds_tests_count = serializers.IntegerField(read_only=True)

    def update(self, instance, validated_data):
        """Uppercase alias name before saving. Raise proper error on duplicated name."""
        if validated_data.get("name"):
            validated_data["name"] = validated_data["name"].upper()
        try:
            return super().update(instance, validated_data)
        except IntegrityError as exc:
            if "package_id, name" in str(exc):
                raise serializers.ValidationError(
                    {
                        "name": "Such sample name already exists.",
                    },
                ) from exc
            raise

    class Meta:
        """Configuration for SampleAlias serializer."""

        model = SampleAlias

        fields = [
            "pk",
            "name",
            "fastq_prefix",
            "verdicts",
            "mic_tests_count",
            "pds_tests_count",
            "match_source",
        ]

        read_only_fields = [
            "pk",
            "fastq_prefix",
            "verdicts",
            "mic_tests_count",
            "pds_tests_count",
            "match_source",
        ]
