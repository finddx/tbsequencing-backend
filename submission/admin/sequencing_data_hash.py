from django.contrib import admin

from submission.models import SequencingDataHash
from .package_sequencing_data_inline import PackageSequencingDataInline


@admin.register(SequencingDataHash)
class SequencingDataHashAdmin(admin.ModelAdmin):
    """Sequencing data hash admin page."""

    inlines = [
        PackageSequencingDataInline,
    ]

    raw_id_fields = [
        "sequencing_data"
    #     "assoc_packages",
    ]

    search_fields = [
        "value",
    ]
