import logging

from django.db import transaction
from django.shortcuts import redirect
from rest_framework import viewsets, serializers, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.reverse import reverse

from submission.models import PackageSequencingData, Package, SequencingData
from submission.permissions import (
    IsParentPackageOwner,
    IsParentPackageEditable,
    ReadOnly,
)
from submission.serializers.package.package_sequencingdata import (
    NestedPackageSequencingDataSerializer,
)
from submission.services.s3bucket import SequencingDataS3BucketService
from submission.util.tag import clear_s3_tag

log = logging.getLogger(__name__)


class PackageSequencingDataViewSet(
    viewsets.GenericViewSet,
    viewsets.mixins.RetrieveModelMixin,
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.DestroyModelMixin,
):
    """API endpoint to manage package sequencing data files."""

    serializer_class = NestedPackageSequencingDataSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        IsParentPackageOwner,
        IsParentPackageEditable | ReadOnly,
    )

    def get_queryset(self):
        """Restrict sequencing data to only package related."""
        return PackageSequencingData.objects.filter(
            package__pk=self.kwargs["package_pk"],
        )

    @action(
        methods=["POST"],
        detail=False,
        url_path="upload-link",
        url_name="uploadlink",
    )
    def upload_link(self, request, **kwargs):  # pylint: disable=unused-argument
        """
        Generate S3 file upload link.

        The file will be uploaded by the path `temporary/{username}_{filename}`.
        Raise serializers.ValidationError, if the file already exists by tmp path,
        means user should send fetch request for that file.
        Also raise serializers.ValidationError, if the file already persisted,
        means user should select another name for a file
        or remove sequencing data object, corresponded to this file.
        """
        serializer: NestedPackageSequencingDataSerializer = self.get_serializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        url = SequencingDataS3BucketService(
            filename=serializer.validated_data["filename"],
            user=request.user,
        ).generate_upload_link()

        return Response({"url": url})

    @action(methods=["POST"], detail=False, url_path="fetch", url_name="fetch")
    def fetch_s3_file(self, request, **kwargs):  # pylint: disable=unused-argument
        """
        Fetch file from S3, validate and generate MD5 hash.

        Return redirect to object details.
        """
        # pylint: disable=too-many-locals

        # passing request into serializer context
        # allows us to generate S3 paths
        serializer: NestedPackageSequencingDataSerializer = self.get_serializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        service = SequencingDataS3BucketService(
            filename=serializer.validated_data["filename"],
            user=request.user,
        )

        try:
            md5_hash, file_size = service.validate_uploaded_file()
        except serializers.ValidationError:
            # remove invalid FASTQ file from S3
            service.remove_tmp_file()
            raise

        # search for existing FASTQ by MD5
        seq_data: SequencingData | None = SequencingData.objects.filter(
            hashes__algorithm__iexact="MD5",
            hashes__value__iexact=md5_hash,
        ).first()

        if not seq_data:
            # not found - create SequencingData and its hash
            with transaction.atomic():
                # make sure we only create new objects
                # if the file is successfully persisted
                seq_data = SequencingData.objects.create(
                    data_location="TB-Kb",  # origin of a file
                    filename=service.persisted_filename,
                    file_path=service.persisted_path,
                    file_size=file_size,
                    sequencing_platform="ILLUMINA",
                    library_preparation_strategy="WGS",
                    library_layout="PAIRED",
                )
                seq_data_hash = seq_data.hashes.create(
                    algorithm="MD5",
                    value=md5_hash,
                )
                # persist fastq file on S3
                service.persist_file(
                    SequencingDataId=str(seq_data.id),
                    OriginalFilename=clear_s3_tag(service.filename),
                    MD5Hash=md5_hash,
                )
            log.info("new fastq uploaded: %s by %s", seq_data, request.user)
        else:
            seq_data_hash = seq_data.hashes.get(
                algorithm="MD5",
                value=md5_hash,
            )
            if seq_data.file_size is None:
                # if file is found but has no file size - updating
                # TODO may be confusing for Sequencing Data with multiple hashes
                # better to save it along with sequencing data hash
                seq_data.file_size = file_size
                seq_data.save()

            log.info("existing fastq uploaded: %s by %s", seq_data, request.user)

        # remove temporary file from S3
        service.remove_tmp_file()

        package = Package.objects.get(pk=self.kwargs["package_pk"])

        if PackageSequencingData.objects.filter(
            package=package,
            sequencing_data=seq_data,
            sequencing_data_hash=seq_data_hash,
        ).exists():
            raise serializers.ValidationError(
                "The file is already attached to the package.",
            )

        # we save original filename within fastq-package M2M
        # in order to match it later by prefix with sample alases
        package_fastq: PackageSequencingData = PackageSequencingData.objects.create(
            package=package,
            sequencing_data=seq_data,
            sequencing_data_hash=seq_data_hash,
            filename=serializer.validated_data["filename"],
        )

        package.mark_changed()

        return redirect(
            reverse(
                "submission:packagesequencingdata-detail",
                (self.kwargs["package_pk"], package_fastq.pk),
                request=request,
            ),
        )

    def perform_destroy(self, instance: PackageSequencingData):
        """Mark parent package as changed on sequencing data unlink."""
        package: Package = instance.package
        super().perform_destroy(instance)
        package.mark_changed()
