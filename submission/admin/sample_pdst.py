from django.contrib import admin

from submission.models import PDSTest


class PhenotypicDrugSusceptibilityTestInline(admin.TabularInline):
    """Package sequencing data inline widget."""

    model = PDSTest
    readonly_fields = [
        "get_drug",
        "get_medium",
        "get_method",
        "concentration",
        "test_result",
        "package"
    ]

    fields = [
        "get_drug",
        "get_medium",
        "get_method",
        "concentration",
        "test_result",
        "package"
    ]

    extra = 0
    max_num = 0
    can_delete = False
    verbose_name_plural = "pDST"
    verbose_name = "Phenotypic drug susceptibility test results"

    @admin.display(description='Drug')
    def get_drug(self, obj):
        """Access drug name"""
        return obj.drug.drug_name

    @admin.display(description='Medium')
    def get_medium(self, obj):
        """Access medium name"""
        return obj.medium.medium_name

    @admin.display(description='Method')
    def get_method(self, obj):
        """Access method name"""
        return obj.method.method_name
