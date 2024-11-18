import logging

from django.shortcuts import redirect
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.reverse import reverse

from submission.models import Package
from submission.permissions import IsPackageEditable, ReadOnly, IsPackageOwner
from submission.serializers.package import PackageSerializer
from submission.services.matching import MatchingService

log = logging.getLogger(__name__)


class PackageViewSet(viewsets.ModelViewSet):
    """API endpoint to manage data submission packages."""

    serializer_class = PackageSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        IsPackageOwner,
        IsPackageEditable | ReadOnly,
    )

    def get_queryset(self):
        """Show only self-owned packages."""
        return Package.objects.filter(owner=self.request.user).order_by("-submitted_on")

    @action(methods=["POST"], detail=True, url_path="match", url_name="match")
    def match(self, request: Request, **kwargs):  # pylint: disable=unused-argument
        """Perform package data matching."""
        package: Package = Package.objects.get(pk=kwargs["pk"])

        if package.matching_state != package.MatchingState.MATCHED:
            # do not perform any matching at all,
            # if there were no changes to its data since it was matched

            MatchingService().execute(
                dict(
                    package=package,
                ),
            )
            log.info("package match done: %s by %s", package, package.owner)

        return redirect(
            reverse("submission:package-detail", (package.pk,), request=request),
        )

    @action(methods=["POST"], detail=True, url_path="submit", url_name="submit")
    def submit(self, request: Request, **kwargs):  # pylint: disable=unused-argument
        """Submit the package for moderation."""
        package: Package = Package.objects.get(pk=kwargs["pk"])

        package.to_pending()
        package.save()

        return redirect(
            reverse("submission:package-detail", (package.pk,), request=request),
        )
