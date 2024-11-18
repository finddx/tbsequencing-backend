from django.contrib import admin

from submission.models import PackageStats


class PackageStatsInline(admin.StackedInline):
    """Attachment inline widget."""

    model = PackageStats
    readonly_fields = [
        "cnt_mic_tests",
        "cnt_mic_drugs",
        "list_mic_drug_codes",
        "cnt_pds_tests",
        "cnt_pds_drug_concentration",
        "cnt_pds_drugs",
        "list_pds_drug_codes",
        "cnt_sample_aliases",
        "cnt_samples_matched",
        "cnt_samples_created",
        "cnt_sequencing_data",
    ]
    exclude = [
        "list_mic_drugs",
        "list_pds_drugs",
        "cnt_messages",
    ]
    extra = 0
    max_num = 0
    can_delete = False
