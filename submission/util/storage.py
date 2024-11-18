from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


# pylint: disable=abstract-method
class FastqStorage(S3Boto3Storage):
    """Base FASTQ S3 storage. Uses different bucket name from settings."""

    def get_default_settings(self):
        """Rewrite bucket name."""
        default_settings = super().get_default_settings()
        default_settings["bucket_name"] = settings.AWS_SEQUENCING_DATA_BUCKET_NAME
        return default_settings


# pylint: disable=abstract-method
class FastqTMPStorage(FastqStorage):
    """
    Temporary S3 storage for sequencing data files.

    Used to store files temporarily
    until they get validated and moved to permanent storage.
    """

    location = "temporary"


# pylint: disable=abstract-method
class FastqPermanentStorage(FastqStorage):
    """
    Permanent S3 storage for sequencing data files.

    Files from that storage are deleted only by user request,
    only if they are uploaded by that user
    and only if they're not linked to any package anymore.
    """

    location = "persistent"
