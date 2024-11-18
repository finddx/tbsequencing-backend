import logging

from django.core.files.storage import default_storage
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from storages.backends.s3boto3 import S3Boto3Storage

from submission.models import Attachment
from submission.util.tag import clear_s3_tag

log = logging.getLogger(__name__)


@receiver(post_save, sender=Attachment)
def push_s3_tags_for_created_attachment(
    sender, **kwargs
):  # pylint: disable=unused-argument
    """Push attachment S3 tags after attachment is saved."""
    if not kwargs["created"]:
        # only when attachment is created
        return

    if not isinstance(default_storage, S3Boto3Storage):
        # push tags only for S3 backend
        return

    attachment: Attachment = kwargs["instance"]
    storage = attachment.file.storage
    client = storage.connection.meta.client

    tags = dict(
        OriginalFilename=clear_s3_tag(attachment.original_filename),
        AttachmentId=attachment.pk,
    )

    client.put_object_tagging(
        Bucket=storage.bucket.name,
        Key=attachment.file.name,
        Tagging={
            "TagSet": [{"Key": k, "Value": str(v)} for k, v in tags.items()],
        },
    )


@receiver([post_save, pre_delete], sender=Attachment)
def log_attachment_created(sender, **kwargs):  # pylint: disable=unused-argument
    """Log attachment creation and deletion."""
    signal = kwargs["signal"]
    if signal == post_save and not kwargs["created"]:
        # only on creation time
        return

    action = {
        post_save: "created",
        pre_delete: "deleted",
    }[signal]

    attachment: Attachment = kwargs["instance"]
    log.info("attachment %s: %s on %s", action, attachment, attachment.package)
