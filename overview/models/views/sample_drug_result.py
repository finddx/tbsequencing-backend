from django.contrib.postgres.fields import DateRangeField
from django.db import models
from django_pgviews import view


SAMPLEDRUGRESULT_SQL = """
with
-- get unique drug-sample-result rows
sample_drug_result_contradictory as (
    select distinct
        sp.drug_id,
        sp.sample_id,
        sp.test_result
    from submission_pdstest sp
        where sp.staging IS FALSE
            and sp.sample_id is not null
),
-- keep drug-sample rows that have only 1 unique test result
sample_drug as (
    select
        drug_id,
        sample_id
    from sample_drug_result_contradictory sdr
    group by drug_id, sample_id
        having count(test_result) = 1
)
-- get sample-drug-result records, that have only 1 unique test result
-- this is base matview for drug/gene overview
SELECT
    sdr.sample_id,
    ss.sampling_date,
    coalesce(max(ssa.country_id), ss.country_id) country_id,
    sdr.drug_id,
    sdr.test_result
FROM sample_drug_result_contradictory sdr
     join sample_drug sd
        on  sd.drug_id = sdr.drug_id
        and sd.sample_id = sdr.sample_id
     join submission_sample ss
        on ss.id = sdr.sample_id
     join submission_samplealias ssa
        on ssa.sample_id=ss.id
GROUP BY
    sdr.sample_id,
    ss.sampling_date,
    ss.country_id,
    sdr.drug_id,
    sdr.test_result
"""


class SampleDrugResult(view.MaterializedView):
    """Sample drug test result materialized view, based on PDS tests."""

    sql = SAMPLEDRUGRESULT_SQL

    # we will use this view for Drug/Gene overview
    # also SampleDrugResultStats matview is based on this matview

    sample = models.ForeignKey("submission.Sample", models.DO_NOTHING)
    drug = models.ForeignKey("genphen.Drug", models.DO_NOTHING)
    country = models.ForeignKey("genphen.Country", models.DO_NOTHING)
    sampling_date = DateRangeField(null=True)
    test_result = models.CharField(max_length=1)  # SRI

    class Meta:
        """Options for a model."""

        managed = False  # Created from a view.
