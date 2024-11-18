from django.contrib.postgres.fields import DateRangeField
from django.db import models
from django.db.models import Sum, F, FloatField
from django.db.models.functions import Cast
from django_pgviews import view


SAMPLEDRUGRESULTSTATS_SQL = """
with fixed_geno as (
    SELECT 
        ss.id sample_id,
        gr.drug_id,
        coalesce(max(ssa.country_id), ss.country_id) country_id,
        ss.sampling_date,
        resistance_flag
    FROM submission_genotyperesistance gr
        JOIN submission_sample ss on ss.id = gr.sample_id
        JOIN submission_samplealias ssa on ssa.sample_id=ss.id
    WHERE gr.version=1
    GROUP BY ss.id, gr.drug_id, ss.country_id, ss.sampling_date, resistance_flag, ss.country_id
)
SELECT
    drug_id,
    country_id,
    sampling_date,
    sum(CASE WHEN test_result = 'S' THEN 1 ELSE 0 END) susceptible,
    sum(CASE WHEN test_result = 'R' THEN 1 ELSE 0 END) resistant,
    sum(CASE WHEN test_result = 'I' THEN 1 ELSE 0 END) intermediate,
    'Pheno' resistance_type
FROM overview_sampledrugresult
GROUP BY drug_id, country_id, sampling_date, resistance_type
UNION
SELECT
    gr.drug_id,
    country_id,
    sampling_date,
    sum(CASE WHEN resistance_flag = 'S' THEN 1 ELSE 0 END) susceptible,
    sum(CASE WHEN resistance_flag = 'R' THEN 1 ELSE 0 END) resistant,
    -- we skip records, flagged "U"
    sum(CASE WHEN resistance_flag = 'I' THEN 1 ELSE 0 END) intermediate,
    'Geno' resistance_type
FROM fixed_geno gr
GROUP BY gr.drug_id, gr.country_id, gr.sampling_date, resistance_type
"""


class SampleDrugResultStatsQuerySet(models.QuerySet):
    """Custom queryset for a view."""

    def resistance_stats(self):
        """Annotate query with S/R/I summed stats."""
        susceptible = F("susceptible")
        resistant = F("resistant")
        intermediate = F("intermediate")
        total = susceptible + resistant + intermediate
        return self.annotate(
            total=Sum(total),
            susceptible=Sum(susceptible),
            resistant=Sum(resistant),
            intermediate=Sum(intermediate),
            ratio_susceptible=Cast(susceptible / total * 100, FloatField()),
            ratio_resistant=Cast(resistant / total * 100, FloatField()),
            ratio_intermediate=Cast(intermediate / total * 100, FloatField()),
        )

    def by_drug(self):
        """Group resistance stats by drug."""
        return self.values("drug").resistance_stats().order_by("drug")

    def by_country(self):
        """Group resistance stats by country."""
        return self.values("country").resistance_stats().order_by("country")


class SampleDrugResultStats(view.MaterializedView):
    """Sample to drug resistance statistics view, based on PDS tests."""

    dependencies = ["overview.SampleDrugResult"]
    sql = SAMPLEDRUGRESULTSTATS_SQL

    objects = SampleDrugResultStatsQuerySet.as_manager()

    class ResistanceType(models.Choices):
        """Resistance type enum."""

        PHENOTYPIC = "Pheno"
        GENOTYPIC = "Geno"

    drug = models.ForeignKey("genphen.Drug", models.DO_NOTHING)
    country = models.ForeignKey("genphen.Country", models.DO_NOTHING)
    sampling_date = DateRangeField(null=True)
    resistance_type = models.CharField(max_length=64, choices=ResistanceType.choices)
    susceptible = models.IntegerField()
    resistant = models.IntegerField()
    intermediate = models.IntegerField()

    class Meta:
        """Options for a model."""

        managed = False  # Created from a view.
