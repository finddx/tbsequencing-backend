from django.contrib import admin

from submission.models import SequencingDataHash


class SequencingDataHashInline(admin.TabularInline):
    """Sequencing data hash inline widget."""

    model = SequencingDataHash
    extra = 0
    max_num = 0
    can_delete = False
    verbose_name_plural = "Sequencing data hashes"
    verbose_name = "Sequencing data hash"
    readonly_fields = [
        "algorithm",
        "value",
    ]
    show_change_link = True
