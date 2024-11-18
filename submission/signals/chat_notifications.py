from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver

from identity.models import User
from submission.models import Message


@receiver(post_save, sender=Message)
def send_email_to_receiver(
    sender, instance: Message, created, **kwargs
):  # pylint: disable-msg=W0613
    """
    Send email with message content to a recipient(s).

    Recipients are:
        - all users with staff rights, when message is from package owner
        - package owner, when message is from anyone else
    """
    if not created:
        return

    name = f"{instance.sender}"

    if instance.sender == instance.package.owner:
        recipients = User.objects.filter(
            is_staff=True,
            email__isnull=False,
        ).values_list(
            "email",
            flat=True,
        )
        if instance.sender.first_name and instance.sender.last_name:
            name = f"{instance.sender.first_name} {instance.sender.last_name}"
    else:
        recipients = [instance.package.owner.email]

    subject = (
        f"[TbKb] New message "
        f"from {name} "
        f"on package {instance.package.name}"
    )

    send_mail(
        subject,
        instance.content,  # TODO render a template here?
        None,
        recipients,
        fail_silently=True,
    )
