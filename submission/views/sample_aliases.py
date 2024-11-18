from django.db.models import OuterRef
from rest_framework import viewsets, mixins, permissions

from submission.models import SampleAlias, Package, MICTest, PDSTest
from submission.permissions import (
    IsParentPackageOwner,
    IsParentPackageEditable,
    ReadOnly,
)
from submission.serializers.package.sample_alias import NestedSampleAliasSerializer
from tbkb.db import SubqueryCount


class PackageSampleAliasesViewSet(
    viewsets.GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
):
    """Package Sample aliases viewset."""

    permission_classes = (
        permissions.IsAuthenticated,
        IsParentPackageOwner,
        IsParentPackageEditable | ReadOnly,
    )
    serializer_class = NestedSampleAliasSerializer

    def get_queryset(self):
        """Only work within current package messages."""
        mic_tests = MICTest.objects.filter(sample_alias=OuterRef("pk"))
        pds_tests = PDSTest.objects.filter(sample_alias=OuterRef("pk"))

        return (
            SampleAlias.objects.filter(package_id=self.kwargs["package_pk"])
            .annotate(
                mic_tests_count=SubqueryCount(mic_tests),
                pds_tests_count=SubqueryCount(pds_tests),
            )
            .order_by("name")
        )

    def perform_update(self, serializer):
        """
        Update sample alias.

        Clear all verdicts on changed alias.
        Mark parent package as changed.
        """
        super().perform_update(serializer)

        package: Package = Package.objects.get(pk=self.kwargs["package_pk"])
        package.mark_changed()
        alias: SampleAlias = serializer.instance
        if alias.verdicts:
            alias.verdicts = []
            alias.save()
