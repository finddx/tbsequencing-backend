import pytest
from django.core.files import File
from rest_framework import serializers

from submission.services.file_import import PackageFileMICImportService


@pytest.mark.parametrize(
    "filename,error_message",
    (
        ("mic_unknown_drug_code.xlsx", "WWW: Unknown drug code."),
        ("mic_wrong_range_value.xlsx", "BDQ: Wrong range at SRR000010: "),
        ("mic_no_tests.xlsx", "No data found"),
    ),
)
def test_validation_errors(
    package_of,
    alice,
    shared_datadir,
    drugs,
    filename,
    error_message,
):  # pylint: disable=unused-argument,too-many-arguments
    """Raise validation error on wrong range value."""
    package = package_of(alice)
    with open(shared_datadir / filename, mode="rb") as file:
        with pytest.raises(serializers.ValidationError) as exc:
            PackageFileMICImportService().execute(
                dict(package=package),
                dict(file=File(file)),
            )
        assert error_message in str(exc)
