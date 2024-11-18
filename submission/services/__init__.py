"""Service layer logic package."""
from abc import ABCMeta

from rest_framework import serializers
from service_objects.services import Service as BaseService


class Service(BaseService, metaclass=ABCMeta):
    """Redefined base service class with drf compatible exception throwing."""

    def service_clean(self):
        """Raise DRF compatible validation error."""
        if not self.is_valid():
            raise serializers.ValidationError(self.errors)
