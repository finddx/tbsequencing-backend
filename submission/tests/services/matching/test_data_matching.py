from datetime import date

import pytest
from psycopg2.extras import DateRange
from rest_framework.exceptions import ValidationError

from genphen.models import Country
from submission.models import Package, SequencingData
from submission.services.matching import MatchingService


def test_empty_package_raises_validation_error(package_of, alice):
    """Try to match empty package raises ValidationError."""
    package = package_of(alice)
    with pytest.raises(ValidationError) as exc:
        MatchingService.execute(dict(package=package))
    assert exc.value.args[0] == "Package has no data"


def test_new_sample_created_from_alias(
    package_of,
    alice,
    new_alias_of,
    new_fastq_of,
    countries,
):  # pylint: disable=unused-argument
    """When new alias matched with new fastq by prefix, new sample is created from the alias."""
    package = package_of(alice)
    country = Country.objects.get(pk="ABW")
    alias = new_alias_of(
        package,
        "SAMPLE1",
        fastq_prefix="12345",
        country=country,
        # somehow DateRange object isn't saved
        sampling_date=("2021-01-01", "2021-12-31"),
    )
    fastq1 = new_fastq_of(package, uploaded_filename="12345_file1.fastq.gz")
    fastq2 = new_fastq_of(package, uploaded_filename="12345_file2.fastq.gz")

    MatchingService.execute(dict(package=package))

    alias.refresh_from_db()
    fastq1.refresh_from_db()
    fastq2.refresh_from_db()

    # assert package.state == package.State.DRAFT

    # new sample is created from alias data
    assert alias.sample.country == country
    assert alias.sample.sampling_date == DateRange(date(2021, 1, 1), date(2021, 12, 31))

    # fastq are linked to same sample that the alias
    assert fastq1.sequencing_data.sample == alias.sample
    assert fastq2.sequencing_data.sample == alias.sample

def test_new_sample_created_from_alias_no_fastq_prefix(
    package_of,
    alice,
    new_alias_of,
    new_fastq_of,
    countries,
):  # pylint: disable=unused-argument
    """When new alias matched with new fastq by prefix, new sample is created from the alias."""
    package = package_of(alice)
    country = Country.objects.get(pk="ABW")
    alias = new_alias_of(
        package,
        "SAMPLE1",
        fastq_prefix=None,
        country=country,
        # somehow DateRange object isn't saved
        sampling_date=("2021-01-01", "2021-12-31"),
    )
    fastq1 = new_fastq_of(package, uploaded_filename="SAMPLE1_R1.fastq.gz")
    fastq2 = new_fastq_of(package, uploaded_filename="SAMPLE1_R2.fastq.gz")

    MatchingService.execute(dict(package=package))

    alias.refresh_from_db()
    fastq1.refresh_from_db()
    fastq2.refresh_from_db()

    # assert package.state == package.State.DRAFT

    # new sample is created from alias data
    assert alias.sample.country == country
    assert alias.sample.sampling_date == DateRange(date(2021, 1, 1), date(2021, 12, 31))

    # fastq are linked to same sample that the alias
    assert fastq1.sequencing_data.sample == alias.sample
    assert fastq2.sequencing_data.sample == alias.sample

def test_new_sample_no_fastq_by_prefix_interrupted(
    package_of,
    alice,
    new_alias_of,
):
    """New alias with prefix and no fastq, matching interrupted."""
    package = package_of(alice)
    alias = new_alias_of(package, "SAMPLE1", fastq_prefix="12345")

    MatchingService.execute(dict(package=package))

    alias.refresh_from_db()

    # package goes back to draft because matching is interrupted
    # UPD service now does not manage package state
    # assert package.state == package.State.DRAFT

    # new sample is created from alias
    assert alias.verdicts == [
        {
            "level": "warning",
            "verdict": "No FASTQ files with such prefix provided",
        },
    ]


def test_different_samples_for_same_prefix_group(
    package_of,
    alice,
    new_alias_of,
    new_fastq_of,
    new_sample,
):
    """If different samples for same fastq prefix group detected, it is an error."""
    package = package_of(alice)
    alias = new_alias_of(package, "SAMPLE1", fastq_prefix="12345")
    fastq1 = new_fastq_of(
        package,
        uploaded_filename="12345_file1.fastq.gz",
        sample=new_sample(),
    )
    fastq2 = new_fastq_of(
        package,
        uploaded_filename="12345_file2.fastq.gz",
        sample=new_sample(),
    )

    MatchingService.execute(dict(package=package))

    fastq1.refresh_from_db()
    fastq2.refresh_from_db()
    alias.refresh_from_db()

    assert (
        fastq1.verdicts
        == fastq2.verdicts
        == [
            {
                "level": "error",
                "verdict": "Some of files with same prefix point to different samples",
            },
        ]
    )
    assert alias.verdicts == [
        {
            "level": "error",
            "verdict": "Some of FASTQ files with such prefix point to different samples",
        },
    ]


def test_fastqs_with_same_prefix_share_same_sample(
    package_of,
    alice,
    new_alias_of,
    new_fastq_of,
    new_sample,
):
    """A sample from fastq prefix group propagates to every fastq from the group."""
    package = package_of(alice)
    sample = new_sample()
    new_alias_of(package, "SAMPLE1", fastq_prefix="PREFIX")
    fastq1 = new_fastq_of(
        package,
        uploaded_filename="prefix_file1.fastq.gz",
        sample=sample,
    )
    fastq2 = new_fastq_of(package, uploaded_filename="prefix_file2.fastq.gz")

    MatchingService.execute(dict(package=package))

    fastq1.refresh_from_db()
    fastq2.refresh_from_db()

    assert fastq1.sequencing_data.sample == fastq2.sequencing_data.sample == sample


def test_mic_pds_tests_associated_with_sample_when_matched(
    package_of,
    alice,
    new_alias_of,
    new_fastq_of,
    new_sample,
):
    """MIC/PDS tests, associated with alias, linked to sample when matched."""
    package = package_of(alice)
    sample = new_sample()
    alias = new_alias_of(package, "SAMPLE1", fastq_prefix="PREFIX")
    new_fastq_of(
        package,
        uploaded_filename="prefix_file1.fastq.gz",
        sample=sample,
    )
    new_fastq_of(
        package,
        uploaded_filename="prefix_file2.fastq.gz",
        sample=sample,
    )

    MatchingService.execute(dict(package=package))

    alias.refresh_from_db()
    assert alias.mic_tests.count() == alias.mic_tests.filter(sample=sample).count()
    assert alias.pds_tests.count() == alias.pds_tests.filter(sample=sample).count()
    assert alias.sample == sample


# pylint: disable=too-many-arguments
@pytest.mark.parametrize("origin", ("NCBI", "SRA"))
def test_match_alias_by_name_among_ncbi_aliases(
    new_package_of,
    alice,
    john,
    new_alias_of,
    new_sample,
    origin,
):
    """Alias is matched by name among NCBI/SRA aliases."""
    ncbi_package = new_package_of(john, origin=origin)
    ncbi_sample = new_sample()
    new_alias_of(ncbi_package, "123qwerty", sample=ncbi_sample)

    package = new_package_of(alice)
    alias = new_alias_of(package, "123QWERTY")

    MatchingService.execute(dict(package=package))

    alias.refresh_from_db()

    assert alias.sample == ncbi_sample


def test_match_alias_by_name_among_fastq_library_names(
    package_of,
    alice,
    new_alias_of,
    new_sample,
):
    """Alias is matched by name among sequencing data "library_name" column."""
    fastq: SequencingData = SequencingData.objects.create(
        library_name="123qwerty",
        sample=new_sample(),
    )

    package = package_of(alice)

    alias = new_alias_of(package, "123QWERTY")

    MatchingService.execute(dict(package=package))

    alias.refresh_from_db()

    assert alias.sample == fastq.sample


def test_match_alias_by_name_among_own_previous_aliases(
    new_package_of,
    alice,
    new_alias_of,
    new_sample,
):
    """Alias is matched by name among aliases, uploaded earlier by the user."""
    first_package = new_package_of(alice, Package.State.ACCEPTED)
    first_alias = new_alias_of(first_package, "SAMPLE33", sample=new_sample())

    second_package = new_package_of(alice)
    second_alias = new_alias_of(second_package, "sample33")

    MatchingService.execute(dict(package=second_package))

    second_alias.refresh_from_db()

    assert second_alias.sample == first_alias.sample


@pytest.mark.parametrize(
    "fastq_num,allowed",
    (
        (1, False),
        (2, True),
        (3, False),
        (4, True),
        (5, False),
        (6, True),
        (7, False),
        (8, False),
    ),
)
def test_2_4_6_amount_of_fastq_files_allowed(
    package_of,
    alice,
    new_fastq_of,
    new_alias_of,
    fastq_num,
    allowed,
):
    """Only 2, 4 and 6 fastqs per prefix allowed."""
    package = package_of(alice)
    new_alias_of(package, "A1", fastq_prefix="prefix")
    for j in range(fastq_num):
        new_fastq_of(
            package,
            uploaded_filename=f"prefix_{j}.fastq.gz",
        )

    MatchingService.execute(dict(package=package))

    fastqs = package.assoc_sequencing_datas.all()

    # we detect that fastq was denied by looking in its verdicts
    assert (
        all(
            (
                "Wrong FASTQ files count for a prefix" not in verdict["verdict"]
                for fastq in fastqs
                for verdict in fastq.verdicts
            ),
        )
        is allowed
    )


def test_mark_fastq_not_used_in_matching(package_of, alice, new_fastq_of):
    """Any fastq, that was not used in matching, marked in verdicts."""
    package = package_of(alice)
    fastq = new_fastq_of(package, "whatever.fastq.gz")
    MatchingService.execute(dict(package=package))

    fastq.refresh_from_db()
    assert fastq.verdicts == [
        {
            "level": "warning",
            "verdict": "was not used in matching",
        },
    ]


def test_rematching_clears_previous_matching_results(
    package_of,
    alice,
    new_alias_of,
    new_fastq_of,
):
    """Rematching clears previous matching results."""
    package = package_of(alice)
    alias1 = new_alias_of(package, "A1", fastq_prefix="gg")
    alias2 = new_alias_of(package, "A2", fastq_prefix="bb")
    new_fastq_of(package, uploaded_filename="gg_1.fastq.gz")
    new_fastq_of(package, uploaded_filename="gg_2.fastq.gz")

    MatchingService.execute(dict(package=package))

    alias1.refresh_from_db()
    assert alias1.sample
    alias1_sample_id = alias1.sample.pk

    alias2.refresh_from_db()
    assert alias2.verdicts == [
        {
            "level": "warning",
            "verdict": "No FASTQ files with such prefix provided",
        },
    ]

    package.refresh_from_db()
    package.matching_state = package.MatchingState.CHANGED
    package.save()

    MatchingService.execute(dict(package=package))

    alias1.refresh_from_db()
    assert alias1.sample

    # another sample here
    assert alias1.sample.pk != alias1_sample_id
    # verdicts are not accumulated
    assert alias2.verdicts == [
        {
            "level": "warning",
            "verdict": "No FASTQ files with such prefix provided",
        },
    ]
