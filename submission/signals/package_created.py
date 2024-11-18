import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from submission.models import Package, PackageStats

log = logging.getLogger(__name__)


@receiver(post_save, sender=Package)
def on_package_created(sender, **kwargs):  # pylint: disable=unused-argument
    """Create package stats record along with a package. Log package creation."""
    if kwargs["created"]:
        # only on creation time
        package: Package = kwargs["instance"]
        PackageStats.objects.create(package=package)
        log.info("package created: %s by %s", package, package.owner)
