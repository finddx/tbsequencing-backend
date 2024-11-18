import logging

from django.contrib.admin.models import LogEntry
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from django.dispatch import receiver

log = logging.getLogger("tbkb.admin")


@receiver(user_logged_in)
def admin_logged_in_callback(
    sender, request, user, **kwargs
):  # pylint: disable=unused-argument
    """Log successful admin authentication."""
    if user.is_superuser or user.is_staff:
        ipaddr = request.META.get("REMOTE_ADDR")
        log.info("admin login: %s via IP %s", user, ipaddr)


@receiver(post_save, sender=LogEntry)
def logentry_changed_callback(sender, **kwargs):  # pylint: disable=unused-argument
    """
    Log every change, that happened in admin area.

    Package state change by admin isn't logged here,
    because it is a custom action that admin triggers.
    It logged in delegate area instead.
    """
    if not kwargs["created"]:
        # When something happens in admin area,
        # a LogEntry record is created
        return

    log_entry: LogEntry = kwargs["instance"]
    target = log_entry.get_edited_object()
    message = log_entry.get_change_message() or str(log_entry)
    user = log_entry.user
    log.info(
        'admin change: %s on %s object "%s" - %s',
        user,
        type(target).__name__,
        target,
        message,
    )
