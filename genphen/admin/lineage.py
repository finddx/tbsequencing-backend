from django.contrib import admin
from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin

from genphen.models import Lineage


class LineageResource(resources.ModelResource):
    """GeneDrugResistanceAssociation model import resource."""

    lineage_numbering = fields.Field(
        column_name="Lineage numbering",
        attribute="lineage_numbering",
    )

    lineage_name = fields.Field(
        column_name="Lineage name",
        attribute="lineage_name",
    )

    class Meta:
        """VariantGradeResource settings."""

        model = Lineage
        exclude = ("id",)
        import_id_fields = ("lineage_numbering", "lineage_name")

class LineageAdmin(ImportExportModelAdmin):
    """VariantGrade model admin panel definition."""

    resource_classes = [LineageResource]

admin.site.register(
    Lineage,
    LineageAdmin,
)
