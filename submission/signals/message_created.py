import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from submission.models import Message

log = logging.getLogger(__name__)


@receiver(post_save, sender=Message)
def update_package_stats_on_new_message(
    sender, **kwargs
):  # pylint: disable=unused-argument
    """Update package stats message counter when new message is created."""
    if kwargs["created"]:
        # only on creation time
        message: Message = kwargs["instance"]
        message.package.stats.update()


@receiver(post_save, sender=Message)
def log_new_message(sender, **kwargs):  # pylint: disable=unused-argument
    """Log every new message."""
    if kwargs["created"]:
        message: Message = kwargs["instance"]
        log.info("new message: %s", message)
