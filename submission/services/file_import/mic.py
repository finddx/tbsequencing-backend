from typing import Optional, List, Tuple
import pandas as pd
from django.core.exceptions import ValidationError
from psycopg2.extras import NumericRange, DateRange
from service_objects import fields as f

from genphen.models import (
    Drug,
    Country,
)
from submission.models import MICTest, SampleAlias, Package, Attachment
from submission.services import Service
from submission.util.range import parse_numeric_range

from .base import PackageFileImportService, BaseRow


class MICRow(BaseRow):
    """Single MIC table row model."""

    class Config:
        """Allow custom field types, such as django models."""

        arbitrary_types_allowed = True

    sample_id: str
    medium: str
    fastq_prefix: Optional[str]
    country: Optional[Country] = None
    sampling_date: Optional[DateRange] = None

    tests: List[Tuple[Drug, NumericRange]]



    """(drug, MIC range)"""

    def iter_tests(self, package: Package, alias: SampleAlias):
        """Create row tests in iterative way."""
        for drug, mic_range in self.tests:
            test = MICTest()
            test.drug = drug
            test.range = mic_range
            test.plate = self.medium
            test.package = package
            test.sample_alias = alias
            yield test


class PackageFileMICImportService(PackageFileImportService):
    """Import MIC data from Excel file (xls/xlsx) into specified package."""

    MODEL_CLASS = MICTest
    SHEET_NAME = "MIC"

    def __init__(self, *args, **kwargs):
        """Cache necessary relation records on startup."""
        super().__init__(*args, **kwargs)

        self.named_columns = self.NAMED_COLUMNS | {
            "DST Method": ("medium", None),
        }

    def locate_columns(self, dataframe):
        """MIC column can be either one of declared columns, or a drug tests column."""
        for colname in dataframe.columns:
            if colname in self.named_columns:
                continue

            if not self._drugs.get(colname.upper()):
                raise ValidationError(
                    f"{colname}: Unknown drug code. Please check the column header values."
                )

    def parse_row(self, row: pd.Series) -> MICRow:
        """Parse raw dataframe row to a valid structure."""
        data = self.parse_row_named_columns(row)

        for colname, val in row.items():
            if colname in self.named_columns:
                continue

            # we already assured columns in .locate_columns
            drug = self._drugs[colname.upper()]

            try:
                mic_range = parse_numeric_range(val)
            except Exception as exc:
                raise ValidationError(
                    f"{colname}: Wrong range at {data['sample_id']}: {exc}.",
                ) from exc

            if mic_range is None:
                # don't add tests without range
                continue

            data["tests"].append((drug, mic_range))
        return MICRow(**data)

    def validate_dataframe(self, dataframe: pd.DataFrame):
        """Validate dataframe."""
        super().validate_dataframe(dataframe)

        # asserting columns
        self.locate_columns(dataframe)

        # asserting data
        empty = True
        for _, row in dataframe.iterrows():
            data = self.parse_row(row)
            if data.tests:
                empty = False
        if empty:
            raise ValidationError("No data found.")

    def import_dataframe(self, dataframe: pd.DataFrame):
        """Perform import of the whole dataframe."""
        # pylint: disable=duplicate-code
        package: Package = self.cleaned_data["package"]
        existing_aliases = package.sample_aliases.distinct("name").in_bulk(
            field_name="name",
        )
        aliases_to_create = {}
        aliases_to_update = []
        all_tests = []

        # 1 iteration - create non-existing samples,
        # update fastq prefix for existing
        for _, raw in dataframe.iterrows():
            row = self.parse_row(raw)

            # update or create alias
            if row.sample_id in existing_aliases:
                alias: SampleAlias = existing_aliases[row.sample_id]
                alias.country = row.country
                if not alias.fastq_prefix and row.fastq_prefix:
                    # update prefix only if it's not present
                    alias.fastq_prefix = row.fastq_prefix
                    aliases_to_update.append(alias)
            else:
                if not row.tests:
                    # do not create alias,
                    # if it does not exist,
                    # and we have no tests for it
                    continue

                alias = row.sample_alias(package)

                if aliases_to_create.get(alias.name):
                    alias = aliases_to_create[alias.name]
                else:
                    print(alias)
                    aliases_to_create[alias.name] = alias

            all_tests.extend(row.iter_tests(package, alias))

        self._import_into_db(
            aliases_to_update,
            ["country", "sampling_date", "fastq_prefix"],
            aliases_to_create.values(),
            all_tests,
        )

    def post_process(self):
        """Save the file as an attachment after successful import."""
        file = self.cleaned_data["file"]

        file = self.watermark_excel_file(file)

        Attachment.objects.create(
            type=Attachment.Type.MIC,
            file=file,
            original_filename=file.name,
            size=file.size,
            package=self.cleaned_data["package"],
        )


class PackageMICDataClearService(Service):
    """Clears imported MIC data."""

    package = f.ModelField(Package, required=True)

    def process(self):
        """Remove all MIC data from a package."""
        package: Package = self.cleaned_data["package"]

        # delete all mic tests
        package.mic_tests.all().delete()

        # delete all empty aliases
        package.sample_aliases.filter(
            pds_tests__isnull=True,
            mic_tests__isnull=True,
        ).delete()

        package.attachments.filter(type=Attachment.Type.MIC).delete()

        package.mark_changed()
