from django.db import models
from django.db.models import Sum
from django_pgviews import view

from genphen.models import Drug


class GeneDrugStatsQueryset(models.QuerySet):
    """GeneDrugStats queryset manager."""

    def with_stats(self):
        """Sum results by drug, variant, gene name, etc."""
        return (
            self
            .select_related("drug__data")
            .values(
                "drug",
                "drug__drug_name",
                "gene_name",
                "nucleodic_ann_name",
                "proteic_ann_name",
                "consequence",
                "variant_id",
                "variant_name",
                "variant_grade",
                "variant_grade_version",
                "gene_db_crossref",
                "start_pos",
                "end_pos",
                "global_frequency",
                "total_counts",
            )
            .order_by("start_pos")
            .annotate(
                resistant_count=Sum("resistant_count"),
                susceptible_count=Sum("susceptible_count"),
                intermediate_count=Sum("intermediate_count"),
            )
        )


OVERVIEW_GENEDRUGSTATS_SQL = """
with overall_samples as (
    select
        count(distinct sample_id)
    from submission_genotype
    -- TODO add freebayes filter here too?
),
variant_samples as (
    select distinct
        variant_id,
        sample_id
    from submission_genotype
    where genotyper = 'freebayes'
        and quality>120
),
global_frequencies as (
    select
        variant_id,
        count(sample_id) total_samples,
        (
            count(sample_id) * 100.0 /
            (select * from overall_samples)
        )::float as global_frequency
    from variant_samples
    group by variant_id
),
fapg_distinct as (
    select distinct
        variant_id,
        drug_id,
        fapg.gene_db_crossref_id,
        predicted_effect,
        nucleotidic_annotation,
        proteic_annotation,
        distance_to_reference
    from genphen_formattedannotationpergene fapg
    join genphen_genedrugresistanceassociation gdra
        on gdra.gene_db_crossref_id=fapg.gene_db_crossref_id
),
variant_drug_test_counts as (
    select
        vs.variant_id,
        sdr.drug_id,
        sum(CASE WHEN test_result = 'S' THEN 1 ELSE 0 END) susceptible_count,
        sum(CASE WHEN test_result = 'R' THEN 1 ELSE 0 END) resistant_count,
        sum(CASE WHEN test_result = 'I' THEN 1 ELSE 0 END) intermediate_count
    from variant_samples vs
    join fapg_distinct
        on fapg_distinct.variant_id=vs.variant_id
    join overview_sampledrugresult sdr
        on vs.sample_id = sdr.sample_id
        and sdr.drug_id=fapg_distinct.drug_id
    group by vs.variant_id, sdr.drug_id
)
select COALESCE(gene_name, locus_tag) gene_name,
       gene_db_crossref,
       start_pos + fapg.distance_to_reference as  start_pos,
       end_pos + fapg.distance_to_reference   as  end_pos,
       fapg.variant_id,
         var.position
         || '-'
         || var.reference_nucleotide
         || '-'
         || var.alternative_nucleotide        as  variant_name,
       fapg.nucleotidic_annotation            as  nucleodic_ann_name,
       fapg.proteic_annotation                as  proteic_ann_name,
       fapg.predicted_effect                  as  consequence,
       gf.total_samples                       as  total_counts,
       gf.global_frequency,
       fapg.drug_id,
       coalesce(vdtc.susceptible_count, 0)    as susceptible_count,
       coalesce(vdtc.resistant_count, 0)      as resistant_count,
       coalesce(vdtc.intermediate_count, 0)   as intermediate_count,
       coalesce(vg.grade::text, 'Ungraded')   as variant_grade,
       vg.grade_version                       as variant_grade_version

from overview_gene gene
    -- join variants (1 gene - m variants).
    -- due to way how the annotation pipeline works,
    -- there might be duplicated records in fapg table,
    -- so we join only distinct records here
    join fapg_distinct fapg
        on fapg.gene_db_crossref_id = gene.gene_db_crossref
    -- join variant data (1-1)
    join genphen_variant var
        on var.variant_id = fapg.variant_id
    -- join variant frequencies (1-1)
    join global_frequencies gf
        on gf.variant_id = fapg.variant_id
    -- join test results (1 variant - m test results for m drugs)
    left join variant_drug_test_counts vdtc
        on vdtc.variant_id = fapg.variant_id
        and vdtc.drug_id = fapg.drug_id
    -- join variant grades (1 variant - m grades for m drugs)
    -- it is implied that final data should be filtered by single grade version
    left join genphen_variantgrade vg
        on vg.variant_id = fapg.variant_id
        and vg.drug_id = fapg.drug_id
"""


class GeneDrugStats(view.MaterializedView):
    """Gene association with drug, full info of drug and gene view."""

    dependencies = [
        "overview.SampleDrugResult",
        "overview.Gene",
    ]

    concurrent_index = """
        gene_db_crossref, variant_id, drug_id,
        nucleodic_ann_name, proteic_ann_name, consequence
        """

    sql = OVERVIEW_GENEDRUGSTATS_SQL

    objects = GeneDrugStatsQueryset.as_manager()

    class Type(models.TextChoices):
        """Resistance type."""

        UPSTREAM = "UPSTREAM"
        SYNONYMOUS = "SYNONYMOUS"
        MISSENSE = "MISSENSE"

    drug = models.ForeignKey(
        Drug,
        on_delete=models.DO_NOTHING
    )
    gene_name = models.CharField(max_length=100)
    gene_db_crossref = models.IntegerField()
    variant_id = models.BigIntegerField(db_index=True)
    variant_name = models.CharField(max_length=1024)
    start_pos = models.IntegerField(null=True)
    end_pos = models.IntegerField(null=True)
    nucleodic_ann_name = models.CharField(max_length=100, db_index=True)
    proteic_ann_name = models.CharField(max_length=100, db_index=True)
    consequence = models.CharField(max_length=50, choices=Type.choices)
    # amount of unique samples, connected with the variant (in genotype)
    total_counts = models.IntegerField()
    # frequency of the variant among all unique samples (in genotype)
    global_frequency = models.FloatField()
    resistant_count = models.IntegerField()
    susceptible_count = models.IntegerField()
    intermediate_count = models.IntegerField()
    variant_grade = models.CharField(max_length=1_024)
    variant_grade_version = models.IntegerField()

    class Meta:
        """GeneDrugStats options class."""

        managed = False  # this is a matview
