"""Tests that are generic for both PDS/MIC tests import services."""
import pytest
from django.core.files import File
from rest_framework import serializers

from submission.services.file_import import (
    PackageFileMICImportService,
    PackageFilePDSTImportService,
)


@pytest.mark.parametrize(
    "filename,error_message",
    (
        ("empty_table.xlsx", "An empty table received."),
        ("duplicated_column_names.xlsx", "duplicated columns: "),
        ("declared_column_missing.xlsx", ": declared column is missing."),
        ("empty_cells_in_mandatory_column.xlsx", ": Empty values in mandatory column."),
        ("broken_excel.xlsx", "Excel file format cannot be determined"),
        ("duplicate_values.xlsx", ": Duplicated values in unique column(s)."),
        ("incorrect_date.xlsx", ": Wrong value at"),
    ),
)
@pytest.mark.parametrize(
    "service_class",
    (PackageFileMICImportService, PackageFilePDSTImportService),
)

# pylint: disable=unused-argument,too-many-arguments
def test_validation_errors_mic(
    package_of,
    alice,
    shared_datadir,
    filename,
    error_message,
    service_class,
    drugs,
):  # pylint: disable=too-many-arguments
    """Test against validation error scenarios."""
    package = package_of(alice)
    with open(shared_datadir / filename, mode="rb") as file:
        with pytest.raises(serializers.ValidationError) as exc:
            service_class().execute(
                dict(package=package),
                dict(file=File(file)),
            )
        assert error_message in str(exc)


# pylint: disable=unused-argument,too-many-arguments
@pytest.mark.parametrize(
    "service_class1,service_class2",
    (
        (PackageFileMICImportService, PackageFilePDSTImportService),
        (PackageFilePDSTImportService, PackageFileMICImportService),
    ),
)
def test_duplicate_fastq_prefix_on_upsert(
    package_of,
    alice,
    shared_datadir,
    drugs,
    growth_mediums,
    countries,
    service_class1,
    service_class2,
):
    """Duplicated fastq prefix, imported from second file for another sample, raises error."""
    package = package_of(alice)
    with open(shared_datadir / "duplicate_fastq_on_upsert.xlsx", mode="rb") as file:
        service_class1().execute(
            dict(package=package),
            dict(file=File(file)),
        )
        with pytest.raises(serializers.ValidationError) as exc:
            service_class2().execute(
                dict(package=package),
                dict(file=File(file)),
            )
        assert "fastq_prefix: Duplicated value" in str(exc)
