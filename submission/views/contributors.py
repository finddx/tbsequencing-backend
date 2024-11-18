from rest_framework import viewsets, permissions

from submission.models import Contributor
from submission.permissions import (
    IsParentPackageOwner,
    IsParentPackageEditable,
    ReadOnly,
)
from submission.serializers.package.contributor import (
    NestedContributorSerializer,
    CreateContributorsSerializer,
)


class PackageContributorViewSet(viewsets.ModelViewSet):
    """Package contributors viewset."""

    permission_classes = (
        permissions.IsAuthenticated,
        IsParentPackageOwner,
        IsParentPackageEditable | ReadOnly,
    )
    serializer_class = NestedContributorSerializer

    def get_serializer(self, *args, **kwargs):
        """Allow bulk creation."""
        if self.action == "create":
            self.serializer_class = CreateContributorsSerializer
        return super().get_serializer(*args, **kwargs)

    def get_queryset(self):
        """Only work within current package messages."""
        return Contributor.objects.filter(package_id=self.kwargs["package_pk"])

    def perform_create(self, serializer: CreateContributorsSerializer):
        """Supply data with package ID."""
        for item in serializer.validated_data["contributors"]:
            item["package_id"] = self.kwargs["package_pk"]
        return super().perform_create(serializer)
