import logging
import re
from typing import List, Tuple, Optional, Dict

import pandas as pd
from django.core.exceptions import ValidationError
from django.core.files import File
from service_objects import fields as f

from psycopg2.extras import DateRange

from genphen.models import (
    PDSAssessmentMethod,
    GrowthMedium,
    Drug,
    Country,
)
from submission.models import PDSTest, SampleAlias, Package, Attachment
from .base import PackageFileImportService, BaseRow
from .. import Service

log = logging.getLogger(__name__)

class PDSTRow(BaseRow):
    """Single pDST table row model."""

    class Config:
        """Allow custom field types, such as django models."""

        arbitrary_types_allowed = True

    sample_id: str
    medium: Optional[GrowthMedium] = None
    assessment: Optional[PDSAssessmentMethod] = None
    tests: List[Tuple[Drug, Optional[str], str]]
    """(drug, concentration or None, result)"""
    sampling_date: Optional[DateRange] = None
    fastq_prefix: Optional[str] = None
    country: Optional[Country] = None
    metadata: Dict[str, str] = {}
    sample_type: Optional[str] = None
    unique_isolate: Optional[str] = None
    host_disease: Optional[str] = None
    fastq: Optional[str] = None
    ngs_instrument: Optional[str] = None

    def iter_tests(self, package: Package, alias: SampleAlias):
        """Create and yield PDS tests based on row data."""
        for drug, concentration, result in self.tests:
            test = PDSTest()
            test.package = package
            test.sample_alias = alias
            test.drug = drug
            test.medium = self.medium
            test.method = self.assessment
            test.concentration = concentration
            test.test_result = result
            # TODO where to route this data
            # self.sample_type
            # self.unique_isolate
            # self.host_disease
            # self.metadata
            # self.fastq
            # self.ngs_instrument
            yield test


class PackageFilePDSTImportService(PackageFileImportService):
    """
    Import pDST/Annex data from Excel file (xls/xlsx) into specified package.

    Table columns:

    Sample Id
        Sample ID
        Unique uppercased together with "DST Method"
    DST Method
        matches genphensql.growth_medium
        unique uppercased together with "Sample Id"
    Country
        public.country match
        2-3-char code or full Country name.
        updates sample.country_id
        optional
    Sampling date
        Number, full year
        updates sample.sampling_date (which is date range)
        optional
    --- Measurements section ---
    "XXX (0[.0] [mg/L])" | "XXX (CC)" +
        Column name contains test conditions data:
        - drug XXX
        - optional concentration (CC if not specified)
        Column values represent test result: S/R/I
    --- Metadata section ---
    Sample type
    Unique isolate
    Host Disease
    FASTQ
    NGS Instrument
    *And any other column, which does not fall into those above,
    treated as metadata column.
    Metadata columns are optional and aren't used.
    """

    MODEL_CLASS = PDSTest
    SHEET_NAME = "PDST"


    COLNAME_REGEX = re.compile(
        r"^([\w\-\/]+)\s*?(?:\(\s*?(?:(\d+(?:[.,]\d+)?)(?:\s*mg/L)?|CC)\s*?\))?$",
    )



    def __init__(self, *args, **kwargs):
        """Cache necessary relation records on startup."""
        super().__init__(*args, **kwargs)

        self.named_columns = self.NAMED_COLUMNS | {
            "DST Method": ("medium", "get_medium"),
            "Assessment method": ("assessment", "get_assessment"),
        }

        self._assessment_methods = {
            p.method_name.upper(): p for p in PDSAssessmentMethod.objects.all()
        }
        self._mediums = {
            m.medium_name.upper(): m for m in GrowthMedium.objects.all()
        }
        self.test_columns = {}

    def locate_test_columns(self, dataframe: pd.DataFrame):
        """
        Locate and pre-cache test columns.

        Since we don't know where those columns might be in the table,
        we look throughout all columns and cache matched.
        This is to be done once at validation stage.
        """
        for column in dataframe.columns:
            if column in self.named_columns:
                continue

            match = self.COLNAME_REGEX.search(column)
            if not match:
                continue

            drug_code, concentration = match.groups()
            try:
                drug = self._drugs[drug_code.upper()]
            except KeyError as exc:
                raise ValidationError(
                    f"{column}: Unknown drug code. Please check the column header values."
                ) from exc
            self.test_columns[column] = (drug, concentration)


    def get_medium(self, val: str) -> GrowthMedium:
        """Parse value as a medium. Raise error, if not found."""
        if not val:
            return None
        return self._mediums[val.strip().upper()]

    def get_assessment(self, val: str) -> PDSAssessmentMethod:
        """Parse value for the assessment method. Returns None if val is none.
        Returns error if val exists and not found."""
        print(val)
        if not val:
            return None
        return self._assessment_methods[val.strip().upper()]

    def get_test_result(self, val: str) -> Optional[str]:
        """Parse value as a test result."""
        result = val.strip().upper()

        if result in ("NA", "N/A", r"N\A", "NONE", "NO", ""):
            return None

        if result not in tuple("SRI"):
            raise ValueError("Unknown test result.")

        return result

    def parse_row(self, row: pd.Series) -> PDSTRow:
        """Parse raw dataframe row to a valid structure."""
        data = self.parse_row_named_columns(row)

        for colname, val in row.items():
            if colname in self.named_columns:
                continue

            if colname not in self.test_columns:
                # add to metadata if it's not a tests column
                data["metadata"][colname] = val
                continue

            try:
                result = self.get_test_result(val)
            except Exception as exc:
                raise ValidationError(
                    f"{colname}: Wrong test result at {row['Sample Id']}.",
                ) from exc

            if not result:
                # do not add tests without result
                continue

            drug, concentration = self.test_columns[colname]
            data["tests"].append((drug, concentration, result))

        return PDSTRow(**data)

    def validate_dataframe(self, dataframe: pd.DataFrame):
        """Validate dataframe."""
        super().validate_dataframe(dataframe)

        self.locate_test_columns(dataframe)

        empty = True
        for _, row in dataframe.iterrows():
            row = self.parse_row(row)
            if row.tests:
                empty = False
        if empty:
            raise ValidationError("No data found.")

    def import_dataframe(self, dataframe: pd.DataFrame):
        """Perform import of the whole dataframe."""
        package: Package = self.cleaned_data["package"]
        existing_aliases = package.sample_aliases.distinct("name").in_bulk(
            field_name="name",
        )
        aliases_to_create = {}
        aliases_to_update = []
        tests = []

        for _, raw in dataframe.iterrows():
            row: PDSTRow = self.parse_row(raw)
            if row.sample_id in existing_aliases:
                # alias already exist, update
                alias: SampleAlias = existing_aliases[row.sample_id]
                alias.country = row.country
                alias.sampling_date = row.sampling_date
                if not alias.fastq_prefix and row.fastq_prefix:
                    alias.fastq_prefix = row.fastq_prefix
                aliases_to_update.append(alias)
            else:
                # alias does not exist, create
                if not row.tests:
                    # don't create alias if it has no tests
                    continue

                alias = row.sample_alias(package)

                if aliases_to_create.get(alias.name):
                    # the alias is already there
                    # (different DST method probably)
                    # TODO check FIND-643 for comments on how to merge data
                    alias = aliases_to_create[alias.name]
                else:
                    aliases_to_create[alias.name] = alias

            tests.extend(row.iter_tests(package, alias))


        self._import_into_db(
            aliases_to_update,
            ["country", "sampling_date", "fastq_prefix"],
            aliases_to_create.values(),
            tests,
        )

    def post_process(self):
        """Save attached file after successful data import."""
        file: File = self.cleaned_data["file"]

        file = self.watermark_excel_file(file)

        Attachment.objects.create(
            type=Attachment.Type.PDS,
            file=file,
            original_filename=file.name,
            size=file.size,
            package=self.cleaned_data["package"],
        )


class PackagePDSDataClearService(Service):
    """Clears imported package PDS data."""

    package = f.ModelField(Package, required=True)

    def process(self):
        """Remove all PDS data from a package."""
        package: Package = self.cleaned_data["package"]

        # delete all pds tests
        package.pds_tests.all().delete()

        # delete all empty aliases
        package.sample_aliases.filter(
            pds_tests__isnull=True,
            mic_tests__isnull=True,
        ).delete()

        package.attachments.filter(type=Attachment.Type.PDS).delete()

        package.mark_changed()
