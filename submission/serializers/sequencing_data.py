from rest_framework import serializers

from submission.models import SequencingData


class SequencingDataSerializer(serializers.ModelSerializer):
    """Sequencing data serializer, that is used in nested view."""

    filename = serializers.RegexField(r"^[\w,\.\s-]+\.fastq\.gz$")
    file_url = serializers.SerializerMethodField(read_only=True)

    def get_file_url(self, instance: SequencingData):
        """Return file S3 url."""
        if instance.filename:
            # we can have no filename on records
            # that come from NCBI
            return instance.filename.url
        return ""

    class Meta:
        """Config class for sequencing data serializer."""

        model = SequencingData
        fields = [
            "pk",
            "filename",  # filename
            "file_path",  # S3 location, with bucket name
            "file_url",  # S3 signed link url
            "file_size",
            "library_name",  # some fixed value, may be sample name
            "data_location",  # S3 location, with bucket name
        ]

        read_only_fields = [
            "library_name",
            "data_location",
            "file_path",
            "file_url",  # S3 signed link url
            "file_size",
        ]
