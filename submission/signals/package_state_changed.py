import logging

from django.dispatch import receiver
from django.utils import timezone
from django_fsm.signals import post_transition

from submission.models import Package

log = logging.getLogger(__name__)


@receiver([post_transition], sender=Package)
def on_package_state_changed(sender, **kwargs):  # pylint: disable=unused-argument
    """
    Update state_changed_on when state is changed.

    Log package status change.
    """
    package: Package = kwargs["instance"]
    package.state_changed_on = timezone.now()
    package.save()
    log.info(
        "status change: %s from %s to %s",
        package,
        kwargs.get("source"),
        kwargs.get("target"),
    )
