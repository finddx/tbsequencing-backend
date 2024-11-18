from django.core.mail import send_mail
from django.dispatch import receiver
from django_fsm.signals import post_transition

from identity.models import User
from submission.models import Package


@receiver([post_transition], sender=Package)
def mark_parent_package_dirty(sender, **kwargs):  # pylint: disable=unused-argument
    """Send an email notification on package state change."""
    target: Package.State = kwargs["target"]
    package: Package = kwargs["instance"]
    owner: User = package.owner

    if target == Package.State.PENDING:
        admin_recipients = User.objects.admins_on_duty().values_list(
            "email",
            flat=True,
        )
        send_mail(
            subject="New data package submission",
            message=f"New data package {package.name!r} has been submitted "
            f"for review by {owner}.",
            from_email=None,
            recipient_list=admin_recipients,
            fail_silently=True,
        )
        return

    if target == Package.State.REJECTED:
        reason = kwargs.get("method_kwargs", {}).get("reason", "-")
        subject = f"Package {package.name!r} has been rejected"
        message = (
            f"Hi {owner}, your package {package.name!r} has been reviewed "
            f"and rejected with reason:\n"
            f"{reason}"
        )
    elif target == Package.State.ACCEPTED:
        subject = f"Package {package.name!r} has been accepted"
        message = (
            f"Hi {owner}, your package {package.name!r} has been reviewed "
            f"and approved."
        )
    else:
        return

    send_mail(
        subject=subject,
        message=message,
        from_email=None,
        recipient_list=[package.owner.email],
        fail_silently=True,
    )
