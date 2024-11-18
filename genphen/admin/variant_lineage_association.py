from django.contrib import admin
from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget

from genphen.models import VariantLineageAssociation, Lineage


class VariantLineageAssociationResource(resources.ModelResource):
    """VariantGrade model import resource."""

    position = fields.Field(
        column_name="Position",
        attribute="position"
    )

    alternative_nucleotide = fields.Field(
        column_name="Alternative Nucleotide",
        attribute="alternative_nucleotide"
    )

    count_presence = fields.Field(
        column_name="Presence",
        attribute="count_presence"
    )

    lineage = fields.Field(
        column_name="Lineage",
        attribute="lineage",
        widget=ForeignKeyWidget(Lineage, field="lineage_numbering")
    )

    class Meta:
        """VariantLineageAssociationResource settings."""

        model = VariantLineageAssociation
        exclude = ("id", "variant")
        import_id_fields = ("position", "alternative_nucleotide", "lineage", "count_presence")



class VariantGradeAdmin(ImportExportModelAdmin):
    """VariantGrade model admin panel definition."""

    resource_classes = [VariantLineageAssociationResource]
    skip_admin_log = True
    readonly_fields=('variant', 'lineage')

admin.site.register(VariantLineageAssociation, VariantGradeAdmin)
