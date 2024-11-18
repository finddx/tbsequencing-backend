import pytest
from django.core.files import File

from submission.models import SampleAlias, Attachment
from submission.services.file_import import (
    PackageFileMICImportService,
    PackageMICDataClearService,
)


def test_imported_tests_count(
    package_of,
    alice,
    shared_datadir,
    drugs,
    countries,
):  # pylint: disable=unused-argument
    """Imported file tests count match actual."""
    with open(shared_datadir / "mic_valid.xlsx", "rb") as file:
        PackageFileMICImportService().execute(
            dict(package=package_of(alice)),
            dict(file=File(file)),
        )

    assert package_of(alice).mic_tests.count() == 30


@pytest.mark.parametrize(
    "sample_name,tests_cnt",
    (("SRR000010", 15), ("SRR000011", 13)),
)
def test_sample_alias_created_and_linked_to_tests(
    package_of,
    alice,
    shared_datadir,
    sample_name,
    tests_cnt,
    drugs,
    countries
):  # pylint: disable=unused-argument,too-many-arguments
    """Every sample ID has an alias, created within package, to which tests are linked."""
    with open(shared_datadir / "mic_valid.xlsx", "rb") as file:
        PackageFileMICImportService().execute(
            dict(package=package_of(alice)),
            dict(file=File(file)),
        )

    sample_alias: SampleAlias = (
        package_of(alice).sample_aliases.filter(name=sample_name).get()
    )
    assert sample_alias.mic_tests.count() == tests_cnt

# for service post-process to work properly
@pytest.mark.django_db(transaction=True)
def test_clear_mic_data(
    package_of,
    alice,
    shared_datadir,
    drugs,
    countries,
):  # pylint: disable=unused-argument
    """MIC tests are cleared along with attachments and aliases."""
    # upload data
    with open(shared_datadir / "mic_valid.xlsx", "rb") as file:
        PackageFileMICImportService().execute(
            dict(package=package_of(alice)),
            dict(file=File(file)),
        )

    assert package_of(alice).mic_tests.count() == 30
    assert package_of(alice).sample_aliases.count() == 3
    assert package_of(alice).attachments.count() == 1

    # clear uploaded data
    PackageMICDataClearService().execute(
        dict(package=package_of(alice)),
    )

    assert package_of(alice).mic_tests.count() == 0
    assert package_of(alice).sample_aliases.count() == 0
    assert package_of(alice).attachments.count() == 0


def test_skip_alias_without_results(
    package_of,
    alice,
    shared_datadir,
    drugs,
    countries,
):  # pylint: disable=unused-argument
    """Do not create alias that has no results in excel."""
    package = package_of(alice)
    filename = "mic_contains_alias_without_results.xlsx"
    with open(shared_datadir / filename, mode="rb") as file:
        PackageFileMICImportService().execute(
            dict(package=package),
            dict(file=File(file)),
        )


def test_existing_alias_updates_fastq_prefix(
    package_of,
    alice,
    shared_datadir,
    new_alias_of,
    drugs,
    countries,
):  # pylint: disable=unused-argument, too-many-arguments
    """Existing alias updates its empty fastq prefix."""
    alias = new_alias_of(package_of(alice), name="SRR000010", fastq_prefix=None)

    with open(shared_datadir / "mic_valid.xlsx", "rb") as file:
        PackageFileMICImportService().execute(
            dict(package=package_of(alice)),
            dict(file=File(file)),
        )

    alias.refresh_from_db()
    assert alias.fastq_prefix == "abc"


# for service post-process to work properly
@pytest.mark.django_db(transaction=True)
def test_attachment_created_after_import(
    package_of,
    alice,
    shared_datadir,
    drugs,
    countries,
):  # pylint: disable=unused-argument
    """Attachment is created after successful excel import."""
    with open(shared_datadir / "mic_valid.xlsx", "rb") as file:
        PackageFileMICImportService().execute(
            dict(package=package_of(alice)),
            dict(file=File(file)),
        )

    attachment: Attachment = package_of(alice).attachments.first()
    assert attachment.type == attachment.Type.MIC
    # here somehow is full path to temp copy of a file
    assert attachment.original_filename.endswith("mic_valid.xlsx")
