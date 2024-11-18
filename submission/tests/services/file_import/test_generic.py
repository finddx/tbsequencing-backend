"""Tests that are generic for both PDS/MIC tests import services."""
import pytest
from django.core.files import File

from genphen.models import Country

from submission.services.file_import import (
    PackageFileMICImportService,
    PackageFilePDSTImportService,
)

FILE_VALID = "pdst1__valid.xlsx"
FILE_VALID_2 = "pdst2__valid.xlsx"

@pytest.mark.parametrize(
    "file_name,sample_name,country_code,service_class",
    (
        (FILE_VALID, "STRAIN1", "FRA", PackageFilePDSTImportService),
        (FILE_VALID, "STRAIN2", "CHE", PackageFilePDSTImportService),
        (FILE_VALID_2, "962-13", "FRA", PackageFilePDSTImportService),
        (FILE_VALID_2, "915-2015", "FRA", PackageFilePDSTImportService),
        (FILE_VALID_2, "901", "CHE", PackageFilePDSTImportService),
        ("mic_valid.xlsx", "SRR000010", "CHE", PackageFileMICImportService),
        ("mic_valid.xlsx", "SRR000011", "FRA", PackageFileMICImportService),
    ),
)
def test_new_sample_has_country(
    package_of,
    alice,
    shared_datadir,
    file_name,
    sample_name,
    country_code,
    service_class,
    drugs,
    countries,
    growth_mediums,
    assessment_methods,
):  # pylint: disable=unused-argument,too-many-arguments
    """New sample has country specified."""
    with open(shared_datadir / file_name, mode="rb") as file:
        service_class().execute(
            dict(package=package_of(alice)),
            dict(file=File(file)),
        )

    sample_alias = package_of(alice).sample_aliases.filter(name=sample_name).get()
    country = Country.objects.filter(three_letters_code=country_code).get()
    assert sample_alias.country == country
