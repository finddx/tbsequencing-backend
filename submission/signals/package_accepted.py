from django.dispatch import receiver
from django_fsm.signals import post_transition

from identity.models import User
from submission.models import Package


@receiver([post_transition], sender=Package)
def unstage_accepted_package_data(sender, **kwargs):  # pylint: disable=unused-argument
    """Mark accepted package MIC/PDS tests, that have matched with sample, as production ready."""
    target: Package.State = kwargs["target"]
    if target != Package.State.ACCEPTED:
        return

    package: Package = kwargs["instance"]
    package.mic_tests.filter(sample__isnull=False).update(staging=False)
    package.pds_tests.filter(sample__isnull=False).update(staging=False)


@receiver([post_transition], sender=Package)
def mark_other_user_packages_as_changed(
    sender, **kwargs
):  # pylint: disable=unused-argument
    """
    Mark user other packages, that are still in DRAFT, as changed.

    This needed in order to preserve data integrity.
    Accepted package can contain data,
    that could be used to match data in other user packages.
    """
    target: Package.State = kwargs["target"]
    if target != Package.State.ACCEPTED:
        return

    package: Package = kwargs["instance"]
    user: User = package.owner

    editable_package: Package
    for editable_package in user.packages.editable():
        editable_package.mark_changed()
