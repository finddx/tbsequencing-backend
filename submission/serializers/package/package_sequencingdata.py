from rest_framework import serializers
from rest_framework_nested.serializers import NestedHyperlinkedModelSerializer
from submission.models import PackageSequencingData
from submission.serializers.sequencing_data import SequencingDataSerializer


class NestedPackageSequencingDataSerializer(NestedHyperlinkedModelSerializer):
    """Package sequencing data serializer, that is used in nested view."""

    parent_lookup_kwargs = {
        "package_pk": "package__pk",
    }

    filename = serializers.RegexField(r"^[\w,\.\s-]+\.fastq\.gz$")
    sequencing_data = SequencingDataSerializer(read_only=True)
    verdicts = serializers.JSONField(read_only=True)

    class Meta:
        """Config class for sequencing data serializer."""

        model = PackageSequencingData
        extra_kwargs = {
            "url": {"view_name": "submission:packagesequencingdata-detail"},
        }
        fields = [
            "pk",
            "url",
            "created_at",
            "filename",
            "sequencing_data",
            "verdicts",
        ]
        read_only_fields = [
            "pk",
            "url",
            "created_at",
            "sequencing_data",
            "verdicts",
        ]
