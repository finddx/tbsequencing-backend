from django.contrib import admin

from ..models import GeneSearchHistory


@admin.register(GeneSearchHistory)
class GeneSearchHistoryAdmin(admin.ModelAdmin):
    """Gene search history admin page."""

    list_display = ("gene_db_crossref_id", "counter", "date")
    readonly_fields = ("date", "gene_db_crossref_id", "counter")
