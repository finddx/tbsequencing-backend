from datetime import date
from dateutil import parser

import pytest
from django.core.files import File
from psycopg2.extras import DateRange

from genphen.models import PDSAssessmentMethod, GrowthMedium
from submission.models import SampleAlias, Attachment
from submission.services.file_import import PackageFilePDSTImportService


FILE_VALID = "pdst1__valid.xlsx"
FILE_VALID_2 = "pdst2__valid.xlsx"
NO_COUNTRY = "pds_no_country.xlsx"
NO_YOI = "pds_no_yoi.xlsx"
CONTAINS_ALIAS_WO_TESTS = "pds_contains_alias_without_results.xlsx"
SAME_NAME_DIFFERENT_DST_METHOD = "pds_same_name_different_dst.xlsx"


@pytest.mark.parametrize(
    "filename,sample_name,start,end",
    (
        (FILE_VALID, "STRAIN1", "2016-01-01", "2017-01-01"),
        (FILE_VALID, "STRAIN2", "2019-01-01", "2020-01-01"),
        (FILE_VALID_2, "962-13", "2011-01-01", "2012-01-01"),
        (FILE_VALID_2, "915-2015", "2011-11-30", "2011-12-01"),
        (FILE_VALID_2, "901", "2010-01-01", "2011-01-01"),
    ),
)
def test_new_sample_has_sampling_date(
    package_of,
    alice,
    shared_datadir,
    drugs,
    growth_mediums,
    assessment_methods,
    countries,
    filename,
    sample_name,
    start,
    end,
):  # pylint: disable=unused-argument,too-many-arguments
    """New sample has sampling date specified from YoI."""
    package = package_of(alice)
    with open(shared_datadir / filename, mode="rb") as file:
        PackageFilePDSTImportService().execute(
            dict(package=package),
            dict(file=File(file)),
        )

    sample_alias = package_of(alice).sample_aliases.filter(name=sample_name).get()
    sampling_date: DateRange = sample_alias.sampling_date

    assert sampling_date == DateRange(
        lower=parser.parse(start).date(),
        upper=parser.parse(end).date(),
        bounds="[)"
    )



@pytest.mark.parametrize(
    "filename,sample_name,medium,method",
    (
        (FILE_VALID_2, "901", "LJ", "Resistance Ratio"),
    ),
)
def test_sample_has_assessment_method(
    package_of,
    alice,
    shared_datadir,
    drugs,
    growth_mediums,
    countries,
    assessment_methods,
    filename,
    sample_name,
    medium,
    method,
):  # pylint: disable=unused-argument,too-many-arguments
    """New sample has country specified."""
    with open(shared_datadir / filename, mode="rb") as file:
        PackageFilePDSTImportService().execute(
            dict(package=package_of(alice)),
            dict(file=File(file)),
        )
    medium_obj = GrowthMedium.objects.filter(medium_name=medium).get()
    print(medium_obj)
    test = package_of(alice).pds_tests.filter(medium=medium_obj.medium_id).get()
    print(test)
    assesment = PDSAssessmentMethod.objects.filter(method_name=method).get()
    print(assesment)
    assert test.method == assesment

@pytest.mark.parametrize(
    "filename,sample_name,tests_cnt",
    (
        (FILE_VALID, "STRAIN1", 14),
        (FILE_VALID, "STRAIN2", 13),
        (FILE_VALID_2, "962-13", 10),
        (FILE_VALID_2, "915-2015", 13),
    ),
)
def test_new_sample_marked_as_created_within_package(
    package_of,
    alice,
    shared_datadir,
    drugs,
    growth_mediums,
    countries,
    assessment_methods,
    filename,
    sample_name,
    tests_cnt,
):  # pylint: disable=unused-argument,too-many-arguments
    """New sample has "created within the package" mark inside its package m2m membership."""
    with open(shared_datadir / filename, mode="rb") as file:
        PackageFilePDSTImportService().execute(
            dict(package=package_of(alice)),
            dict(file=File(file)),
        )

    sample_alias: SampleAlias = (
        package_of(alice).sample_aliases.filter(name=sample_name).get()
    )
    assert sample_alias.pds_tests.count() == tests_cnt


@pytest.mark.parametrize(
    "filename,test_count",
    (
        (FILE_VALID, 27),
        (FILE_VALID_2, 25),
    ),
)
def test_imported_tests_count(
    package_of,
    alice,
    shared_datadir,
    drugs,
    growth_mediums,
    assessment_methods,
    countries,
    filename,
    test_count,
):  # pylint: disable=unused-argument,too-many-arguments
    """Imported file tests count match actual."""
    with open(shared_datadir / filename, mode="rb") as file:
        PackageFilePDSTImportService().execute(
            dict(package=package_of(alice)),
            dict(file=File(file)),
        )

    assert package_of(alice).pds_tests.count() == test_count


def test_alias_without_country(
    package_of,
    alice,
    shared_datadir,
    drugs,
    growth_mediums,
):  # pylint: disable=unused-argument
    """Alias imported without country."""
    with open(shared_datadir / NO_COUNTRY, mode="rb") as file:
        PackageFilePDSTImportService().execute(
            dict(package=package_of(alice)),
            dict(file=File(file)),
        )

    alias: SampleAlias = package_of(alice).sample_aliases.first()
    assert alias.country is None


def test_alias_without_year_of_isolation(
    package_of,
    alice,
    shared_datadir,
    drugs,
    growth_mediums,
):  # pylint: disable=unused-argument
    """Alias imported without year of isolation."""
    with open(shared_datadir / NO_YOI, mode="rb") as file:
        PackageFilePDSTImportService().execute(
            dict(package=package_of(alice)),
            dict(file=File(file)),
        )

    alias: SampleAlias = package_of(alice).sample_aliases.first()
    assert alias.sampling_date is None


def test_alias_inherits_country_and_yoi(
    package_of,
    alice,
    new_alias_of,
    shared_datadir,
    drugs,
    growth_mediums,
    countries,
):  # pylint: disable=unused-argument,too-many-arguments
    """Existing alias inherits country and year of isolation."""
    existing_alias = new_alias_of(package_of(alice), "STRAIN1")

    with open(shared_datadir / FILE_VALID, mode="rb") as file:
        PackageFilePDSTImportService().execute(
            dict(package=package_of(alice)),
            dict(file=File(file)),
        )
    existing_alias.refresh_from_db()
    assert existing_alias.country.three_letters_code == "FRA"
    assert existing_alias.sampling_date == DateRange(date(2016, 1, 1), date(2017, 1, 1))


def test_skip_alias_without_test_results(
    package_of,
    alice,
    shared_datadir,
    drugs,
    growth_mediums,
):  # pylint: disable=unused-argument
    """Do not create alias, if it has no test results."""
    with open(shared_datadir / CONTAINS_ALIAS_WO_TESTS, mode="rb") as file:
        PackageFilePDSTImportService().execute(
            dict(package=package_of(alice)),
            dict(file=File(file)),
        )

    assert package_of(alice).sample_aliases.filter(name="STRAIN1").count() == 1
    assert package_of(alice).sample_aliases.filter(name="STRAIN2").count() == 0


def test_same_alias_different_dst_method(
    package_of,
    alice,
    shared_datadir,
    drugs,
    growth_mediums,
):  # pylint: disable=unused-argument
    """Allow duplicate sample IDs, if they have different DST methods."""
    with open(shared_datadir / SAME_NAME_DIFFERENT_DST_METHOD, mode="rb") as file:
        PackageFilePDSTImportService().execute(
            dict(package=package_of(alice)),
            dict(file=File(file)),
        )

    assert package_of(alice).sample_aliases.count() == 1
    assert package_of(alice).pds_tests.count() == 17


# for service post-process to work properly
@pytest.mark.django_db(transaction=True)
def test_attachment_created_after_import(
    package_of,
    alice,
    shared_datadir,
    drugs,
    growth_mediums,
    countries,
):  # pylint: disable=unused-argument,too-many-arguments
    """Attachment created on successful excel upload."""
    with open(shared_datadir / FILE_VALID, "rb") as file:
        PackageFilePDSTImportService().execute(
            dict(package=package_of(alice)),
            dict(file=File(file)),
        )

    attachment: Attachment = package_of(alice).attachments.first()
    assert attachment.type == attachment.Type.PDS
    # here somehow is full path to temp copy of a file
    assert attachment.original_filename.endswith(FILE_VALID)
