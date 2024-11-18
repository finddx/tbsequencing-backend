from django.contrib import admin

from submission.models import Sample
from .sample_pdst import PhenotypicDrugSusceptibilityTestInline
from .sample_mic import MinimumInhibitoryConcentrationValueInline
from .sample_alias import SampleAliasInline

@admin.register(Sample)
class SampleAdmin(admin.ModelAdmin):
    """Sequencing data hash admin page."""

    read_only_fields = [
        "get_biosample_link"
    ]

    list_display = [
        "id",
        "get_biosample_link",
        "submission_date",
        # "country",
        # "get_alias_biosample",
        # "get_alias_sequencing_biosample",
        # "get_other_aliases",
        # "get_scientific_species_name",
        "bioanalysis_status",
        "origin",
    ]

    raw_id_fields = [
        "ncbi_taxon",
    ]

    search_fields = [
        "aliases__name",
        "=id",
        "=biosample_id"
    ]

    list_filter = [
        "country",
        "bioanalysis_status",
        "origin",
    ]

    inlines = [
        SampleAliasInline,
        PhenotypicDrugSusceptibilityTestInline,
        MinimumInhibitoryConcentrationValueInline,
    ]


    def get_deleted_objects(self, objs, request):
        deleted_objects, model_count, perms_needed, protected = (
            super().get_deleted_objects(objs, request)
        )
        for obj in objs:
            deleted_objects.extend(
                [str(x) for x in obj.sequencing_data_set.filter(sample=obj)]
            )
            deleted_objects.extend(
                [str(x) for x in obj.aliases.filter(sample=obj)]
            )
            model_count["Sample aliass"] = (
                model_count.get("Sample aliass", 0) + obj.aliases.filter(sample=obj).count()
            )
            model_count["Sequencing data"] = (
                model_count.get("Sequencing data", 0)
                + obj.sequencing_data_set.filter(sample=obj).count()
            )

        return deleted_objects, model_count, perms_needed, protected


    def delete_model(self, request, obj):
        #Cascading deletion on sequencing data+alias
        obj.sequencing_data_set.filter(sample=obj).delete()
        obj.aliases.filter(sample=obj).delete()
        super().delete_model(request, obj)
