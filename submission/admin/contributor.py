from django.contrib import admin

from submission.models import Contributor

class ContributorInline(admin.TabularInline):
    """Inline display in the package view."""
    model = Contributor
    extra = 0
    max_num = 0
    can_delete = False
    verbose_name_plural = "Contributors"
    verbose_name = "Contributor"
    show_change_link = False

    fields = [
        "first_name",
        "last_name",
        "role"
    ]

    readonly_fields = [
        "first_name",
        "last_name",
        "role"
    ]
