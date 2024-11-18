from rest_framework import viewsets, mixins, permissions

from submission.models import Message
from submission.permissions import IsParentPackageOwner
from submission.serializers.message import MessageSerializer


class PackageMessagesViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
):
    """
    Package messages views.

    Authenticated user only allowed to read messages from its own package.
    When user creates a message, he becomes a sender of the message.
    """

    permission_classes = (
        permissions.IsAuthenticated,
        IsParentPackageOwner,
    )
    serializer_class = MessageSerializer

    def get_queryset(self):
        """Only work within current package messages."""
        return Message.objects.filter(package_id=self.kwargs["package_pk"])

    def perform_create(self, serializer):
        """Create message from serializer data."""
        serializer.instance = Message.objects.create(
            sender=self.request.user,
            package=self.request.user.packages.get(
                pk=self.kwargs["package_pk"],
            ),
            content=serializer.validated_data["content"],
        )
