import pytest
from django.core.files import File
from rest_framework import serializers

from submission.services.file_import import PackageFilePDSTImportService

NO_SAMPLING_DATE = "pds_unknown_drug_code.xlsx"
UNKNOWN_TEST_RESULT = "pds_unknown_test_result.xlsx"
UNKNOWN_COUNTRY = "pds_unknown_country.xlsx"
ZERO_TESTS = "pds_zero_tests.xlsx"


def test_unknown_drug_code(package_of, alice, shared_datadir):
    """Raise validation error on unknown drug code."""
    package = package_of(alice)
    with open(shared_datadir / NO_SAMPLING_DATE, mode="rb") as file:
        with pytest.raises(serializers.ValidationError) as exc:
            PackageFilePDSTImportService().execute(
                dict(package=package),
                dict(file=File(file)),
            )
        assert "HHH (0.1): Unknown drug code. Please check the column header values." in str(exc)


def test_unknown_test_result(
    package_of,
    alice,
    shared_datadir,
    drugs,
    growth_mediums,
):  # pylint: disable=unused-argument
    """Raise validation error on unknown test result."""
    with open(shared_datadir / UNKNOWN_TEST_RESULT, mode="rb") as file:
        with pytest.raises(serializers.ValidationError) as exc:
            PackageFilePDSTImportService().execute(
                dict(package=package_of(alice)),
                dict(file=File(file)),
            )
        assert "INH (0.1): Wrong test result at STRAIN1" in str(exc)


def test_unknown_country(
    package_of,
    alice,
    shared_datadir,
    drugs,
):  # pylint: disable=unused-argument
    """Raise validation error on unknown country."""
    with open(shared_datadir / UNKNOWN_COUNTRY, mode="rb") as file:
        with pytest.raises(serializers.ValidationError) as exc:
            PackageFilePDSTImportService().execute(
                dict(package=package_of(alice)),
                dict(file=File(file)),
            )
        assert "Country: Wrong value at STRAIN1" in str(exc)


def test_zero_results(
    package_of,
    alice,
    shared_datadir,
    drugs,
    growth_mediums,
):  # pylint: disable=unused-argument
    """Raise validation error on zero PDS test results."""
    with open(shared_datadir / ZERO_TESTS, mode="rb") as file:
        with pytest.raises(serializers.ValidationError) as exc:
            PackageFilePDSTImportService().execute(
                dict(package=package_of(alice)),
                dict(file=File(file)),
            )
        assert "No data found" in str(exc)
