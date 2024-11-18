import gzip
import hashlib
import logging
import os
import tempfile
import uuid
from typing import Tuple

import boto3
from Bio.SeqIO.QualityIO import FastqGeneralIterator
from botocore.config import Config
from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from identity.models import User
from submission.exceptions import Conflict
from submission.util.storage import FastqTMPStorage, FastqPermanentStorage

log = logging.getLogger(__name__)


class SequencingDataS3BucketService:
    """Service for handling sequencing data files on S3."""

    def __init__(self, filename: str, user: User):
        """Serve single file."""
        self.filename = filename
        self.user = user
        self._persisted_filename = None
        self.bucket_name = settings.AWS_SEQUENCING_DATA_BUCKET_NAME
        self.client = boto3.client("s3", config=Config(signature_version="s3v4"))
        self.tmp_storage = FastqTMPStorage(
            bucket_name=self.bucket_name,
        )
        self.persisted_storage = FastqPermanentStorage(
            bucket_name=self.bucket_name,
        )

    @property
    def persisted_filename(self):
        """Generate and preserve random unique filename."""
        if not self._persisted_filename:
            parts = self.filename.split(".", 1)
            self._persisted_filename = f"{uuid.uuid4().hex}.{parts[1]}"
        return self._persisted_filename

    @property
    def persisted_path(self):
        """Full persisted path on S3 bucket."""
        return f"{self.persisted_storage.location}/{self.persisted_filename}"

    @property
    def tmp_filename(self):
        """
        Name of the file in temporary folder on S3.

        We prefix it with User PK to avoid collisions between user files.
        """
        return f"{self.user.pk}_{self.filename}"

    @property
    def tmp_path(self):
        """Full temporary path on S3 bucket."""
        return f"{self.tmp_storage.location}/{self.tmp_filename}"

    def generate_upload_link(self) -> str:
        """Check if file already exist on s3, return file upload link if not."""
        if self.tmp_storage.exists(self.tmp_filename):
            # special case, when FE needs to skip s3 upload
            # and go directly to .validate_uploaded_file
            raise Conflict("file is already uploaded, proceed to fetch directly.")

        return self.client.generate_presigned_url(
            ClientMethod="put_object",
            Params=dict(
                Bucket=self.tmp_storage.bucket_name,  # pylint: disable=no-member
                Key=self.tmp_path,
            ),
        )

    def validate_uploaded_file(self) -> Tuple[str, int]:
        """Validate uploaded file, return MD5 hash of the contents of the file."""
        if not self.tmp_storage.exists(self.tmp_filename):
            raise NotFound("file is not found on S3.")

        # pylint: disable=unexpected-keyword-arg
        md5_hash = hashlib.md5(usedforsecurity=False) # nosemgrep: bandit.B303-1

        # download the file, calculate MD5 in parallel
        with (
            self.tmp_storage.open(self.tmp_filename) as cloud_file,
            tempfile.NamedTemporaryFile(mode="wb", delete=False) as t_file,
        ):
            while chunk := cloud_file.read(1024 * 512):
                t_file.write(chunk)
                # calculate MD5 on GZIPPED file
                md5_hash.update(chunk)

            md5_hex_digest = md5_hash.hexdigest()
            local_tmp_file_path = t_file.name

        # verifying file structure
        sequences = 0
        file_size = os.path.getsize(local_tmp_file_path)
        file = gzip.open(local_tmp_file_path, mode="rt", encoding="utf-8")

        try:
            for _ in FastqGeneralIterator(file):
                sequences += 1

            if not sequences:
                raise ValueError("no sequences found in the FASTQ file")

        except Exception as exc:
            raise serializers.ValidationError({"uploaded_file": str(exc)}) from exc

        finally:
            # close and remove temporary file
            file.close()
            os.remove(local_tmp_file_path)

        return md5_hex_digest, file_size

    def persist_file(self, **tags):
        """
        Move file from temporary directory to persistent.

        Put arbitrary tags on the object before copy.
        """
        self.client.copy(
            dict(
                Bucket=self.tmp_storage.bucket_name,  # pylint: disable=no-member
                Key=self.tmp_path,
            ),
            self.persisted_storage.bucket_name,  # pylint: disable=no-member
            self.persisted_path,
        )

        # put tagging on file in persistent dir
        for _ in range(3):
            response = self.client.put_object_tagging(
                Bucket=self.persisted_storage.bucket_name,  # pylint: disable=no-member
                Key=self.persisted_path,
                Tagging={
                    "TagSet": [{"Key": k, "Value": v} for k, v in tags.items()],
                },
            )
            if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
                log.warning("Failed to put tagging on FASTQ file: %s", response)
            else:
                break

    def remove_tmp_file(self):
        """Remove file from persisted location."""
        self.tmp_storage.delete(self.tmp_filename)
