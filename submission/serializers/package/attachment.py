from rest_framework import serializers

from submission.models import Attachment


class AttachmentSerializer(serializers.ModelSerializer):
    """Package attachment model serializer."""

    class Meta:
        """Options for package attachment model serializer."""

        model = Attachment
        fields = [
            "pk",
            "created_at",
            "type",
            "file",
            "size",
            "original_filename",
        ]
