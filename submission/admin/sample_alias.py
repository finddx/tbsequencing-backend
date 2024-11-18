from django.contrib import admin

from submission.models import SampleAlias

@admin.register(SampleAlias)
class SampleAliasAdmin(admin.ModelAdmin):
    """Sequencing data hash admin page."""

    raw_id_fields = [
        "sample"
    #     "assoc_packages",
    ]

    search_fields = [
        "name",
    ]

    verbose_name_plural = "Sample aliases"


class SampleAliasInline(admin.TabularInline):
    """Inline display in the sample view."""
    model = SampleAlias
    extra = 0
    max_num = 0
    can_delete = False
    verbose_name_plural = "Sample aliases"
    verbose_name = "Sample alias"
    show_change_link = False
    fields = [
        "package",
        "name",
        "origin",
        "origin_label",
        "match_source"
    ]

    readonly_fields = [
        "package",
        "name",
        "origin",
        "origin_label",
        "match_source"
    ]
