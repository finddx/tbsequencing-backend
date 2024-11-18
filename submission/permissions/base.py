from rest_framework.permissions import BasePermission, SAFE_METHODS


class ReadOnly(BasePermission):
    """Allow only read-only actions."""

    def has_permission(self, request, view):
        """Check the permission."""
        return request.method in SAFE_METHODS
