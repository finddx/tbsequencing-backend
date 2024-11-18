from django.contrib import admin
from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget

from genphen.models import PromoterDistance
from biosql.models import Dbxref


class PromoterDistanceResource(resources.ModelResource):
    """GeneDrugResistanceAssociation model import resource."""


    gene_db_crossref = fields.Field(
        column_name="Locus tag",
        attribute="gene_db_crossref",
        widget=ForeignKeyWidget(Dbxref, field="data__locus_tag"),
    )

    start = fields.Field(
        column_name="Start",
        attribute="start"
    )

    end = fields.Field(
        column_name="End",
        attribute="end"
    )

    class Meta:
        """VariantGradeResource settings."""

        model = PromoterDistance
        exclude = ("id",)
        import_id_fields = ("gene_db_crossref", "start", "end")

class PromoterDistanceAdmin(ImportExportModelAdmin):
    """VariantGrade model admin panel definition."""

    resource_classes = [PromoterDistanceResource]

admin.site.register(
    PromoterDistance,
    PromoterDistanceAdmin,
)
