from itertools import cycle

import pytest

from genphen.models import (
    FormattedAnnotationPerGene,
    Variant,
    GeneDrugResistanceAssociation,
    VariantGrade,
)
from overview.models import SampleDrugResult
from overview.models.views import GeneDrugStats
from submission.models import Genotype


@pytest.fixture
def annotations(alice_package, drugs):
    """Generate all required data to have something in GeneDrugStats matview."""
    # pylint: disable=redefined-outer-name
    samples = []
    drug = drugs[0]
    for i in range(20):
        alice_package.new_sample()
        alice_package.new_alias(f"A{i}", sample=alice_package.sample)
        alice_package.new_pds_test(
            result="S",
            concentration=0.5,
            staging=False,
            drug=drug,
        )
        samples.append(alice_package.sample)

    for i in [1, 2]:
        Variant.objects.create(
            variant_id=i,
            chromosome=f"NC_000001.{i}",
            position=2160000 + i,
            reference_nucleotide="TAGA",
            alternative_nucleotide="GTAA",
        )
        VariantGrade.objects.create(
            variant_id=i,
            drug=drug,
            grade=i,
            grade_version=1,
        )

    # genotype for every sample,
    # so we will have accumulated data by gene variant
    for i, variant_id in zip(range(20), cycle([1, 2])):
        Genotype.objects.create(
            sample_id=samples[i].id,
            variant_id=variant_id,
            genotyper="freebayes",  # matters
            quality=150,
            reference_ad=530,
            alternative_ad=510,
            total_dp=900,
            genotype_value="ABCDEF",
        )

    # annotation for every variant
    annotations_list = [
        FormattedAnnotationPerGene.objects.create(
            variant_id=variant_id,
            gene_db_crossref_id=10,
            predicted_effect="UPSTREAM",
            nucleotidic_annotation="AAA",
            proteic_annotation="BBB",
            distance_to_reference=distance,
        )
        for variant_id, distance in [(1, 78), (2, 141)]
    ]

    GeneDrugResistanceAssociation.objects.create(
        gene_db_crossref_id=10,
        drug=drug,
        tier=1,
    )

    SampleDrugResult.refresh()
    GeneDrugStats.refresh()

    return annotations_list
