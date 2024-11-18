from django.contrib import admin
from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget

from genphen.models import GeneDrugResistanceAssociation, Drug
from biosql.models import Dbxref


class GeneDrugResistanceAssociationResource(resources.ModelResource):
    """GeneDrugResistanceAssociation model import resource."""

    drug = fields.Field(
        column_name="Drug name",
        attribute="drug",
        widget=ForeignKeyWidget(Drug, field="drug_name"),
    )

    gene_db_crossref = fields.Field(
        column_name="Locus tag",
        attribute="gene_db_crossref",
        widget=ForeignKeyWidget(Dbxref, field="data__locus_tag"),
    )

    tier = fields.Field(
        column_name="Tier",
        attribute="tier"
    )

    class Meta:
        """VariantGradeResource settings."""

        model = GeneDrugResistanceAssociation
        exclude = ("id",)
        import_id_fields = ("drug", "gene_db_crossref", "tier")

class GeneDrugResistanceAssociationAdmin(ImportExportModelAdmin):
    """VariantGrade model admin panel definition."""

    resource_classes = [GeneDrugResistanceAssociationResource]

admin.site.register(
    GeneDrugResistanceAssociation,
    GeneDrugResistanceAssociationAdmin,
)
