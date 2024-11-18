from django.contrib import admin

from submission.models import Attachment


class AttachmentInline(admin.TabularInline):
    """Attachment inline widget."""

    model = Attachment
    readonly_fields = [
        "type",
        "file",
        "original_filename",
        "size",
    ]
    extra = 0
    max_num = 0
    can_delete = False


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    """Attachment admin page."""

    readonly_fields = [
        "type",
        "file",
        "original_filename",
        "size",
        "package",
    ]
