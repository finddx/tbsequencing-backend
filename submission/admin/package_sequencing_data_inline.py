from django.contrib import admin

from submission.models import PackageSequencingData


class PackageSequencingDataInline(admin.TabularInline):
    """Package sequencing data inline widget."""

    model = PackageSequencingData
    readonly_fields = [
        "package",
        "sequencing_data",
        "sequencing_data_hash",
        "filename",
        "created_at",
        "verdicts",
    ]
    extra = 0
    max_num = 0
    can_delete = False
    verbose_name_plural = "Sequencing data files"
    verbose_name = "Sequencing data file"
    show_change_link = True
