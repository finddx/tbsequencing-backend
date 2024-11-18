from rest_framework import serializers

from submission.models import Package
from .attachment import AttachmentSerializer


# pylint: disable=duplicate-code
class PackageSerializer(serializers.HyperlinkedModelSerializer):
    """Package model serializer for REST API."""

    attachments = AttachmentSerializer(many=True, read_only=True)

    sequencing_data = serializers.HyperlinkedIdentityField(
        view_name="submission:packagesequencingdata-list",
        lookup_url_kwarg="package_pk",
    )
    mic_tests = serializers.HyperlinkedIdentityField(
        view_name="submission:mictest-list",
        lookup_url_kwarg="package_pk",
    )
    pds_tests = serializers.HyperlinkedIdentityField(
        view_name="submission:pdstest-list",
        lookup_url_kwarg="package_pk",
    )
    sample_aliases = serializers.HyperlinkedIdentityField(
        view_name="submission:samplealias-list",
        lookup_url_kwarg="package_pk",
    )
    messages = serializers.HyperlinkedIdentityField(
        view_name="submission:message-list",
        lookup_url_kwarg="package_pk",
    )
    contributors = serializers.HyperlinkedIdentityField(
        view_name="submission:contributor-list",
        lookup_url_kwarg="package_pk",
    )
    messages_count = serializers.IntegerField(
        source="stats.cnt_messages",
        read_only=True,
    )
    mic_tests_count = serializers.IntegerField(
        source="stats.cnt_mic_tests",
        read_only=True,
    )
    pds_tests_count = serializers.IntegerField(
        source="stats.cnt_pds_tests",
        read_only=True,
    )
    sample_aliases_count = serializers.IntegerField(
        source="stats.cnt_sample_aliases",
        read_only=True,
    )
    sequencing_data_count = serializers.IntegerField(
        source="stats.cnt_sequencing_data",
        read_only=True,
    )
    mic_drugs = serializers.ListField(
        child=serializers.CharField(),
        source="stats.list_mic_drug_codes",
        read_only=True,
    )
    mic_drugs_count = serializers.IntegerField(
        source="stats.cnt_mic_drugs",
        read_only=True,
    )
    pds_drugs = serializers.ListField(
        child=serializers.CharField(),
        source="stats.list_pds_drug_codes",
        read_only=True,
    )
    pds_drugs_count = serializers.IntegerField(
        source="stats.cnt_pds_drugs",
        read_only=True,
    )
    pds_drug_concentration_count = serializers.IntegerField(
        source="stats.cnt_pds_drug_concentration",
        read_only=True,
    )

    def create(self, validated_data):
        """Assign current authenticated user as package owner."""
        validated_data["owner"] = self.context["request"].user
        return super().create(validated_data)

    class Meta:
        """Configuration for PackageSerializer."""

        model = Package
        extra_kwargs = {
            "url": {"view_name": "submission:package-detail"},
        }
        fields = [
            "pk",
            "url",
            "name",
            "description",
            "origin",
            "matching_state",
            "state",
            "state_changed_on",
            "rejection_reason",
            "attachments",
            "messages_count",
            "messages",
            "sequencing_data",
            "sequencing_data_count",
            "mic_tests",
            "mic_tests_count",
            "mic_drugs",
            "mic_drugs_count",
            "pds_tests",
            "pds_tests_count",
            "pds_drugs_count",
            "pds_drug_concentration_count",
            "pds_drugs",
            "sample_aliases",
            "sample_aliases_count",
            "contributors",
        ]
        read_only_fields = [
            "pk",
            "url",
            "matching_state",
            "state",
            "state_changed_on",
            "rejection_reason",
            "attachments",
            "messages",
            "messages_count",
            "sequencing_data",
            "sequencing_data_count",
            "mic_tests",
            "mic_drugs",
            "pds_tests",
            "pds_drugs",
            "sample_aliases",
            "sample_aliases_count",
            "contributors",
        ]
