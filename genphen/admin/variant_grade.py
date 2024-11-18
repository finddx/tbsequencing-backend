import logging

from django.contrib import admin
from django.db import connection
from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin
from import_export.instance_loaders import CachedInstanceLoader
from import_export.widgets import ForeignKeyWidget

from genphen.models import VariantGrade, Drug

log = logging.getLogger("tbkb.admin")

TABLENAME = "genphen_variantgrade"


class CachedQueryset:
    """
    Object, behaving like queryset, with only `get` method.

    In conjunction with CachingForeignKeyWidget used to cache foreign key data.
    """

    def __init__(self, cache: dict):
        """Initialize with actual queryset data."""
        self._cache = cache

    def get(self, **kwargs):
        """Act like `.get` method of actual queryset."""
        cache_key = tuple(kwargs.values())[0]
        return self._cache[cache_key]


class CachingForeignKeyWidget(ForeignKeyWidget):
    """ForeignKeyWidget, that caches All related model data."""

    def __init__(self, *args, **kwargs):
        """Initialize widget with cache property."""
        super().__init__(*args, **kwargs)
        self._cache = None

    def get_queryset(self, value, row, *args, **kwargs):
        """Return QuerySet-like object, that returns cached results."""
        if not self._cache:
            queryset = super().get_queryset(value, row, *args, **kwargs)
            data = {getattr(v, self.field): v for v in queryset}
            self._cache = data
        return CachedQueryset(self._cache)


class VariantGradeResource(resources.ModelResource):
    """VariantGrade model import resource."""

    position = fields.Field(
        column_name="Position",
        attribute="position"
    )

    drug = fields.Field(
        column_name="Drug name",
        attribute="drug",
        widget=CachingForeignKeyWidget(Drug, field="drug_name"),
    )

    alternative_nucleotide = fields.Field(
        column_name="Alternative Nucleotide",
        attribute="alternative_nucleotide"
    )

    reference_nucleotide = fields.Field(
        column_name="Reference Nucleotide",
        attribute="reference_nucleotide"
    )


    grade = fields.Field(column_name="Grade", attribute="grade")
    grade_version = fields.Field(column_name="Grade version", attribute="grade_version")

    class Meta:
        """VariantGradeResource settings."""

        model = VariantGrade
        exclude = ("id", "variant")
        import_id_fields = (
            "drug",
            "position",
            "reference_nucleotide",
            "alternative_nucleotide",
            "grade",
            "grade_version"
        )

        use_bulk = True
        # skip_diff = True
        # force_init_instance = True
        instance_loader_class = CachedInstanceLoader

    def after_import(self, dataset, result, using_transactions, dry_run, **kwargs):
        """Log successful import."""
        super().after_import(dataset, result, using_transactions, dry_run)
        if not dry_run:
            log.info(
                f"%d records imported into {TABLENAME} by %s",
                result.total_rows,
                kwargs.get("user"),
            )


@admin.action(description=f"! TRUNCATE {TABLENAME} table")
def truncate_variant_grade(
    modeladmin,
    request,
    queryset,
):  # pylint: disable=unused-argument
    """Truncate genphen_variantgrade table."""
    cursor = connection.cursor()
    cursor.execute(f"TRUNCATE TABLE {TABLENAME}")

    log.warning("%s is truncated by %s", TABLENAME, request.user)


class VariantGradeAdmin(ImportExportModelAdmin):
    """VariantGrade model admin panel definition."""

    resource_classes = [VariantGradeResource]
    skip_admin_log = True
    actions = [truncate_variant_grade]
#    readonly_fields=('variant', "drug", "grade", "grade_version")
    raw_id_fields = ('variant',)


admin.site.register(VariantGrade, VariantGradeAdmin)
