# pylint: disable=duplicate-code
from django.shortcuts import redirect
from rest_framework import viewsets, mixins, permissions
from rest_framework.decorators import action
from rest_framework.reverse import reverse

from submission.models import Package
from submission.permissions import (
    IsParentPackageOwner,
    IsParentPackageEditable,
    ReadOnly,
)
from submission.serializers.package.mic_tests import MICTestsSerializer
from submission.services.file_import.mic import (
    PackageFileMICImportService,
    PackageMICDataClearService,
)


class PackageMICTestsViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
):
    """Package MIC tests."""

    permission_classes = (
        permissions.IsAuthenticated,
        IsParentPackageOwner,
        IsParentPackageEditable | ReadOnly,
    )
    serializer_class = MICTestsSerializer

    def create(self, request, *args, **kwargs):
        """Import Excel file with data."""
        package = Package.objects.get(pk=self.kwargs["package_pk"])

        PackageFileMICImportService().execute(
            dict(package=package),
            request.FILES,
        )

        return redirect(
            reverse("submission:package-detail", (package.pk,), request=request),
        )

    @action(methods=["POST"], detail=False, url_name="clear", url_path="clear")
    def clear(self, request, **kwargs):  # pylint: disable=unused-argument
        """Clear imported data."""
        package = Package.objects.get(pk=self.kwargs["package_pk"])

        PackageMICDataClearService().execute(
            dict(package=package),
        )

        return redirect(
            reverse("submission:package-detail", (package.pk,), request=request),
        )
