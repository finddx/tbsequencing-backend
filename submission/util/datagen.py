from datetime import date
from decimal import Decimal

from psycopg2.extras import DateRange, NumericRange

from genphen.models import Drug, PDSAssessmentMethod
from biosql.models import Taxon
from ..models import Sample, Package


class PackageGenerator:
    """Submission package data generator, used for testing."""

    def __init__(self, user, name="Le Package"):
        """Initialize generator with data."""
        self.package, _ = Package.objects.get_or_create(
            owner=user,
            name=name,
        )
        self.samples = []
        self.last_sample = None
        self.aliases = []
        self.last_alias = None

    def new_sample(
        self,
        country: str = None,
        yoi: int = None,
    ):
        """Create and add sample to sample list."""
        sample = self.package.samples.create(
            ncbi_taxon=Taxon.objects.first(),
            country_id=country,
            sampling_date=DateRange(date(yoi, 1, 1), date(yoi, 12, 31))
            if yoi
            else None,
        )
        self.last_sample = sample
        return sample

    @property
    def sample(self) -> Sample:
        """Return last sample from sample list, create if not exists."""
        if not self.last_sample:
            return self.new_sample(
                country="FRA",
                yoi=2022,
            )
        return self.last_sample

    def new_alias(
        self,
        name: str,
        sample: Sample = None,
        fastq_prefix: str = None,
        country: str = None,
        yoi: int = None,
    ):  # pylint: disable=too-many-arguments
        """Create and add alias to alias list."""
        alias = self.package.sample_aliases.create(
            name=name,
            sample=sample,
            fastq_prefix=fastq_prefix,
            country=country,
            sampling_date=DateRange(date(yoi, 1, 1), date(yoi, 12, 31))
            if yoi
            else None,
        )
        self.last_alias = alias
        return alias

    @property
    def alias(self):
        """Return latest created alias, create if not exist."""
        if not self.last_alias:
            return self.new_alias(
                name="ALIAS1",
                sample=self.sample,
            )
        return self.last_alias

    def new_pds_test(
        self,
        result: str,
        concentration: float = None,
        staging: bool = True,
        drug_name: str = None,
        drug: Drug = None,
    ):  # pylint: disable=too-many-arguments
        """Create pds test and add it to pds tests list."""
        pdst = self.alias.pds_tests.create(
            test_result=result,
            drug=drug
            or Drug.objects.filter(
                synonyms__drug_name_synonym__iexact=drug_name,
            ).first(),
            concentration=concentration,
            method=PDSAssessmentMethod.objects.first(),
            package=self.alias.package,
            sample=self.alias.sample,
            staging=staging,
        )
        return pdst

    def new_mic_test(
        self,
        drug_name: str = None,
        drug: Drug = None,
        staging=True,
        range_from=0,
        range_to=1,
    ):  # pylint: disable=too-many-arguments
        """Create and return new MIT test."""
        mic = self.alias.mic_tests.create(
            package=self.alias.package,
            sample=self.alias.sample,
            plate="A PLATE",
            range=NumericRange(Decimal(range_from), Decimal(range_to)),
            staging=staging,
            drug=drug
            or Drug.objects.filter(
                synonyms__drug_name_synonym__iexact=drug_name,
            ).first(),
        )
        return mic
