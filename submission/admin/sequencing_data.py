from django.contrib import admin

from submission.models import SequencingData
from .sequencing_data_hash_inline import SequencingDataHashInline


@admin.register(SequencingData)
class SequencingDataAdmin(admin.ModelAdmin):
    """Sequencing data admin page."""

    inlines = [
        SequencingDataHashInline,
    ]

    list_display = [
        "__str__",
        "get_library_url",
        # "get_filenames",
        "created_at",
    ]

    readonly_fields = [
        "file_size",
        "file_path",
        "filename",
    ]

    raw_id_fields =[
        "sample"
    ]

    list_filter = [
        "data_location",
        "s3_storage_class",
    ]

    search_fields = [
        "library_name",
        "=id",
        "assoc_packages__filename",
    ]
