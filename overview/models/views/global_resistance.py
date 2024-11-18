from django.db import models
from django.db.models import F, Case, When, Value
from django_pgviews import view


class GlobalResistanceStatsQuerySet(models.QuerySet):
    """GlobalResistanceStats custom queryset."""

    def with_ratios(self):
        """Annotate with ratios, follow old naming."""
        total = F("total_samples")
        # pylint: disable=unnecessary-lambda-assignment
        total_ratio = lambda field: Case(
            When(total_samples=0, then=Value(0.0)),
            default=field / total * 100.0,
        )
        return self.values(
            "total_samples",
            "mono_resistant",
            "poly_resistant",
            "multidrug_resistant",
            "extensive_drug_resistant",
            "rifampicin_resistant",
        ).annotate(
            ratio_mono_res=total_ratio(F("mono_resistant")),
            ratio_poly_res=total_ratio(F("poly_resistant")),
            ratio_multi_drug_res=total_ratio(F("multidrug_resistant")),
            ratio_ext_drug_res=total_ratio(F("extensive_drug_resistant")),
            ratio_rif_res=total_ratio(F("rifampicin_resistant")),
        )


GLOBALRESISTANCESTATS_SQL = """
with resistant as (
    select
        sample_id,
        array_agg(drug_name) drug_arr
    from overview_sampledrugresult r
        join genphen_drug d on d.drug_id = r.drug_id
    where r.test_result = 'R'
    group by sample_id
),

-- Mono-resistance:
-- resistance to one first-line anti-TB drug only
mono_resistant as (
    select *
    from resistant
    where drug_arr::text[] in (
                       array ['Ethambutol'],
                       array ['Isoniazid'],
                       array ['Pyrazinamide'],
                       array ['Rifampicin']
                      )
),

-- Poly-resistance:
-- resistance to more than one first-line anti-TB drug,
-- other than both isoniazid and rifampicin
poly_resistant as (
    select *
    from resistant
    where (select count(*) from (
        select unnest(drug_arr)
        intersect
        select unnest(array ['Ethambutol', 'Isoniazid', 'Pyrazinamide', 'Rifampicin'])
    ) intersection ) > 1
        and drug_arr::text[] != array ['Isoniazid', 'Rifampicin']
),

-- Multi-drug resistance (MDR):
-- resistance to at least both isoniazid and rifampicin
multidrug_resistant as (
    select *
    from resistant
    -- where left array is included in drug_arr
    where array ['Isoniazid', 'Rifampicin'] <@ drug_arr::text[]
),

-- Extensive drug resistance (XDR):
-- resistance to any fluoroquinolone, and at least one of three second-line injectable drugs
-- (capreomycin, kanamycin and amikacin), in addition to multidrug resistance
extensive_drug_resistant as (
    select *
    -- all MDR
    from multidrug_resistant
    -- that fluoroquinolone resistant
    where array ['Fluoroquinolones'] <@ drug_arr::text[]
    -- and at least one of three second-line injectable resistant
    and array ['Capreomycin', 'Kanamycin', 'Amikacin']  && drug_arr::text[]
),

-- Rifampicin resistance (RR):
-- resistance to rifampicin detected using phenotypic or genotypic methods,
-- with or without resistance to other anti-TB drugs.
-- It includes any resistance to rifampicin,
-- in the form of mono-resistance, poly-resistance, MDR or XDR.
rifampicin_resistant as (
    -- selecting from overview_sample_drug_result_stats
    -- because it has genotypic data too
    select count(resistant)
    from overview_sampledrugresultstats osdrs
    join genphen_drug d on d.drug_id = osdrs.drug_id
    where d.drug_name = 'Rifampicin'
)

select
    (select count(*) from submission_sample)        total_samples,
--     (select count(*) from resistant)                total_sum,
    (select count(*) from mono_resistant)           mono_resistant,
    (select count(*) from poly_resistant)           poly_resistant,
    (select count(*) from multidrug_resistant)      multidrug_resistant,
    (select count(*) from extensive_drug_resistant) extensive_drug_resistant,
    (select * from rifampicin_resistant)            rifampicin_resistant
"""


class GlobalResistanceStats(view.MaterializedView):
    """
    Single-record view with global sample stats for TB drug-resistance.

    Reference link:
    https://www.who.int/teams/global-tuberculosis-programme/diagnosis-treatment/treatment-of-drug-resistant-tb/types-of-tb-drug-resistance
    """

    dependencies = [
        "overview.SampleDrugResult",
        "overview.SampleDrugResultStats",
    ]
    sql = GLOBALRESISTANCESTATS_SQL

    class Meta:
        """Meta class."""

        managed = False

    objects = GlobalResistanceStatsQuerySet.as_manager()

    total_samples = models.IntegerField()
    mono_resistant = models.IntegerField()
    poly_resistant = models.IntegerField()
    multidrug_resistant = models.IntegerField()
    extensive_drug_resistant = models.IntegerField()
    rifampicin_resistant = models.IntegerField()
