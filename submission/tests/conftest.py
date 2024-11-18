from hashlib import md5
from uuid import uuid4

import pytest
from psycopg2.extras import DateRange

from genphen.models import Country
from identity.models import User
from submission.models import (
    Package,
    Sample,
    SampleAlias,
    PackageSequencingData,
    SequencingData,
)


@pytest.fixture
def new_alias_of(db):  # pylint: disable=invalid-name,unused-argument
    """Create new sample alias, create a mic and pds test for it."""
    # pylint: disable=too-many-arguments
    def _new_alias_of(
        package: Package,
        name: str,
        fastq_prefix: str = None,
        country: Country = None,
        sampling_date: DateRange = None,
        sample: Sample = None,
    ) -> SampleAlias:
        """Workload function."""
        return package.sample_aliases.create(
            name=name,
            fastq_prefix=fastq_prefix,
            country=country,
            sampling_date=sampling_date,
            sample=sample,
        )

    return _new_alias_of


@pytest.fixture
def new_fastq_of(db):  # pylint: disable=invalid-name,unused-argument
    """Create new sequencing data record, link it to a package."""

    def _new_fastq_of(
        package: Package,
        uploaded_filename: str,
        library_name: str = "",
        sample: Sample = None,
    ) -> PackageSequencingData:
        """Actual function."""
        fastq = SequencingData.objects.create(
            library_name=library_name,
            sample=sample,
            data_location="TB-Kb",
        )
        fastq_hash = fastq.hashes.create(
            algorithm="MD5",
            value=md5(uuid4().bytes, usedforsecurity=False).hexdigest(), # nosec B303
        )
        package_fastq: PackageSequencingData = PackageSequencingData.objects.create(
            package=package,
            sequencing_data=fastq,
            sequencing_data_hash=fastq_hash,
            filename=uploaded_filename,
        )
        return package_fastq

    return _new_fastq_of


@pytest.fixture
def new_package_of(db):  # pylint: disable=invalid-name,unused-argument
    """Create new package."""

    def _new_package_of(
        user: User,
        state: Package.State = Package.State.DRAFT,
        origin: str = None,
    ) -> Package:
        """Actual function."""
        package: Package = user.packages.create(
            name=f"{user.first_name} empty package",
            description=f"{user.get_full_name()} empty from the start submission package",
        )
        package.state = state
        package.origin = origin or package.origin
        package.save()
        return package

    return _new_package_of


@pytest.fixture
def package_of(
    db,
    new_package_of,
):  # pylint: disable=invalid-name,unused-argument,redefined-outer-name
    """
    Create, cache, and return selected users package.

    Only one package per user is maintained.
    """

    def _package_of(
        user,
        state: Package.State = Package.State.DRAFT,
        origin: str = None,
    ) -> Package:
        """Actual working function."""
        if not getattr(_package_of, "data", None):
            _package_of.data = {}
        if not _package_of.data.get(user.pk):
            _package_of.data[user.pk] = new_package_of(user, state, origin)
        return _package_of.data[user.pk]

    return _package_of
