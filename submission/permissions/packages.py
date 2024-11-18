from rest_framework import permissions, status

from submission.models import Package


class IsParentPackageOwner(permissions.BasePermission):
    """
    Current user should own package he is trying to work on.

    Permission for nested endpoints of a package.
    """

    message = {
        "detail": "User should own the package.",
        "status": status.HTTP_403_FORBIDDEN,
    }

    def has_permission(self, request, view):
        """Has permission."""
        return request.user.packages.filter(pk=view.kwargs["package_pk"]).exists()


class IsParentPackageEditable(permissions.BasePermission):
    """
    Check whether parent package is editable, which is DRAFT or REJECTED.

    Permission for nested endpoints of a package endpoint.
    """

    message = {
        "detail": "The package cannot be edited.",
        "status": status.HTTP_403_FORBIDDEN,
    }

    def has_permission(self, request, view):
        """Check permission."""
        return (
            Package.objects.editable()
            .filter(
                pk=view.kwargs["package_pk"],
            )
            .exists()
        )


class IsPackageEditable(permissions.BasePermission):
    """
    Check whether package is editable, which is DRAFT or REJECTED state.

    Permission for the package endpoint.
    """

    message = {
        "detail": "The package cannot be edited.",
        "status": status.HTTP_403_FORBIDDEN,
    }

    def has_object_permission(self, request, view, obj: Package):
        """Check object permission."""
        return obj.state in (
            obj.State.DRAFT,
            obj.State.REJECTED,
        )


class IsPackageOwner(permissions.BasePermission):
    """
    Check whether current user owns the package.

    Permission for the package endpoint.
    """

    message = {
        "detail": "User should own the package.",
        "status": status.HTTP_403_FORBIDDEN,
    }

    def has_object_permission(self, request, view, obj: Package):
        """Check object permission."""
        return request.user == obj.owner
