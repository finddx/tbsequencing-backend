import re
import tempfile
from abc import ABCMeta, abstractmethod
from io import BytesIO
from pathlib import Path
from typing import Type, Iterable, Optional
from datetime import date
from dateutil import parser
from pydantic import BaseModel

from psycopg2.extras import DateRange
import openpyxl
import openpyxl.drawing.image
import pandas as pd
from django import forms
from django.contrib.staticfiles import finders
from django.core.exceptions import ValidationError
from django.core.files import File
from django.db import IntegrityError
from django.db.models import Model
from rest_framework import serializers
from service_objects import fields as f

from genphen.models import (
    DrugSynonym,
    Country,
    Drug,
)

from submission.models import Package, SampleAlias
from submission.services import Service


class BaseRow(BaseModel):
    """Single pDST table row model."""

    class Config:
        """Allow custom field types, such as django models."""

        arbitrary_types_allowed = True

    def sample_alias(self, package):
        """Return sample alias based on data from the row."""
        return SampleAlias(
            package=package,
            name=self.sample_id,
            fastq_prefix=self.fastq_prefix,
            country=self.country,
            sampling_date=self.sampling_date,
        )


class PackageFileImportService(Service, metaclass=ABCMeta):
    """Base class for any package file import service."""

    MODEL_CLASS: Type[Model]
    """MICTest/PDSTest"""

    SHEET_NAME: str = None


    MANDATORY_COLUMNS = [
        "Sample Id",
        "DST Method",
    ]

    NON_NULL_COLUMNS = [
        "Sample Id"
    ]

    FORCE_CASE_COLUMNS = [
        "Sample Id",
        "DST Method",
    ]

    UNIQUE_COLUMNS = [
        ["Sample Id", "DST Method"],
        ["FASTQ prefix"],
    ]

    NAMED_COLUMNS = {
        "Sample Id": ("sample_id", lambda x: x.strip()),
        "Country": ("country", "get_country"),
        "Sampling date": ("sampling_date", "get_sampling_date"),
        "Sample type": ("sample_type", None),
        "Unique isolate": ("unique_isolate", None),
        "FASTQ prefix": ("fastq_prefix", None),
        "Host disease": ("host_disease", None),
        "FASTQ": ("fastq", None),
        "NGS Instrument": ("ngs_instrument", None),
    }

    package = f.ModelField(Package, required=True)
    file = forms.FileField(required=True)

    def __init__(self, *args, **kwargs):
        """Cache necessary relation records on startup."""
        super().__init__(*args, **kwargs)
        self._drugs = {
            ds.drug_name_synonym.upper(): ds.drug for ds in DrugSynonym.objects.all()
        } | {
            ds.drug_name.upper(): ds for ds in Drug.objects.all()
        }

        self._countries = {}
        for country in Country.objects.all():
            if country.two_letters_code:
                self._countries[country.two_letters_code.upper()] = country
            if country.three_letters_code:
                self._countries[country.three_letters_code.upper()] = country
            if country.country_usual_name:
                self._countries[country.country_usual_name.upper()] = country
            if country.country_official_name:
                self._countries[country.country_official_name.upper()] = country

        self.test_columns = {}


    def get_sampling_date(self, val: str) -> Optional[DateRange]:
        """Return range formated sampling date."""
        returned_date = None
        if val.strip():
            # Try to validate a DateRange expression first
            date_range_matched = re.match(
                r'([\[\(])(\d{4}-\d{2}-\d{2}),(\d{4}-\d{2}-\d{2})([\)\]])',
                val.replace(" ", "")
            )
            if date_range_matched:
                lbound, start, end, ubound = date_range_matched.groups()
                returned_date = DateRange(
                    lower=parser.parse(start).date(),
                    upper=parser.parse(end).date(),
                    bounds=lbound+ubound
                )
            if re.match(r'^[0-9]{4}$', val.strip()):
                year = int(val.strip())
                returned_date = DateRange(
                    lower=date(year=year, month=1, day=1),
                    upper=date(year=year, month=12, day=31),
                    bounds="[]",
                )
            if re.match(r'^[0-9]{4}-[0-9]{1,2}$', val.strip()):
                year, month = [int(x) for x in val.strip().split("-")]
                returned_date = DateRange(
                    lower=date(year=year, month=month, day=1),
                    upper=date(year=year+(month//12), month=(month%12)+1, day=1),
                    bounds="[)",
                )
            if re.match(r'^[0-9]{4}-[0-9]{1,2}-[0-9]{1,2}$', val.strip()):
                year, month, day = [int(x) for x in val.strip().split("-")]
                returned_date = DateRange(
                    lower=date(year=year, month=month, day=day),
                    upper=date(year=year, month=month, day=day),
                    bounds="[]",
                )
        if returned_date and returned_date.lower>date.today():
            raise ValidationError("A sampling date in the future was received.")
        return returned_date


    def get_country(self, val: str) -> Optional[Country]:
        """Parse value as a country."""
        country_code = val.strip().upper()
        if country_code:
            return self._countries[country_code]
        return None

    def get_dataframe(self, file: File) -> pd.DataFrame:
        """Parse file into valid dataframe."""
        return pd.read_excel(
            file,
            sheet_name=self.SHEET_NAME,
            dtype="string",
            mangle_dupe_cols=True,
        ).fillna("")

    def validate_dataframe(self, dataframe: pd.DataFrame):
        """
        Validate dataframe.

        This runs within file validation routine,
        so any ValidationError thrown will be considered as file validation error.
        """

        if dataframe.shape[0] < 1:
            # At least 1 row expected
            raise ValidationError("An empty table received.")

        dataframe.columns = dataframe.columns.str.strip()

        dupe_cols = [col for col in dataframe.columns if col.endswith(".1")]
        if dupe_cols:
            # Column names should be unique
            # This check relies on mangle_dupe_cols=True when reading table
            raise ValidationError(
                f"duplicated columns: {', '.join([col.strip('.1') for col in dupe_cols])}",
            )

        # for declared_col in self.DECLARED_COLUMNS:
        #     if declared_col not in dataframe.columns:
        #         raise ValidationError(f"{declared_col}: declared column is missing.")

        for mandatory_col in self.MANDATORY_COLUMNS:
            if mandatory_col not in dataframe.columns:
                raise ValidationError(f"{mandatory_col}: declared column is missing.")
            # mandatory value columns check
            # since we have all types as strings here,
            # we can check empty and whitespace values like that
            empty_values = ~dataframe[mandatory_col].str.strip().astype(bool)
            if mandatory_col in self.NON_NULL_COLUMNS and not dataframe[empty_values].empty:
                raise ValidationError(
                    f"{mandatory_col}: Empty values in mandatory column.",
                )

        for fc_col in self.FORCE_CASE_COLUMNS:
            # UPPERCASE column values to detect case sensitive duplicates
            dataframe[fc_col] = dataframe[fc_col].str.upper()

        unique_col: Iterable
        for unique_col in self.UNIQUE_COLUMNS:
            if len(unique_col)==len(list(set(unique_col) & set(dataframe.columns))):
                group = dataframe.groupby(unique_col).size().reset_index(name="_freq_")
                freq_gt_1 = group["_freq_"] > 1
                all_non_empty = group[unique_col].apply(all, axis=1)
                dupes = group[freq_gt_1 & all_non_empty]
                if not dupes.empty:
                    raise ValidationError(
                        f"{unique_col}: Duplicated values in unique column(s).",
                    )

    def parse_row_named_columns(self, row):
        """Parse row common attributes for MIC and PDST"""
        data = {
            "sample_id": row["Sample Id"],
            "medium": row["DST Method"],
            "fastq_prefix":
              row["FASTQ prefix"].strip().rstrip("_") if row.get("FASTQ prefix")
               else None,
            "tests": [],
            "metadata" : {},
        }

        for row_col, (data_col, parse_func) in self.named_columns.items():
            if row_col in row:
                if parse_func:
                    if isinstance(parse_func, str):
                        parse_func = getattr(self, parse_func)
                    try:
                        data[data_col] = parse_func(data.get(data_col, row[row_col]))
                    except Exception as exc:
                        raise ValidationError(
                            f"{row_col}: Wrong value at {row['Sample Id']}: {row[row_col]}.",
                        ) from exc
                else:
                    data[data_col] = data.get(data_col, row[row_col]) or None
        return data

    @abstractmethod
    def import_dataframe(self, dataframe: pd.DataFrame):
        """Perform actual data import."""

    def clean_file(self):
        """Validate file content."""
        try:
            dataframe = self.get_dataframe(self.cleaned_data["file"])
        except Exception as exc:
            raise ValidationError(exc) from exc
        self.validate_dataframe(dataframe)
        return self.cleaned_data["file"]

    def process(self):
        """Import data into a corresponding model table in a single transaction."""
        package = self.cleaned_data["package"]
        self.cleaned_data["package"] = Package.objects.select_for_update(
            nowait=True,
        ).get(pk=package.pk)

        dataframe = self.get_dataframe(self.cleaned_data["file"])
        self.import_dataframe(dataframe)

        # mark package as changed if it was matched before
        package.mark_changed()

    def _import_into_db(
        self,
        aliases_to_update,
        aliases_fields_to_update,
        aliases_to_create,
        tests,
    ):
        """Import all the created models into database."""
        try:
            SampleAlias.objects.bulk_update(
                aliases_to_update,
                aliases_fields_to_update,
                batch_size=5_000,
            )
            SampleAlias.objects.bulk_create(
                aliases_to_create,
                batch_size=5_000,
            )
        except IntegrityError as exc:
            raise detect_error(exc)  # pylint: disable=raise-missing-from

        self.MODEL_CLASS.objects.bulk_create(
            tests,
            batch_size=5_000,
        )

    @staticmethod
    def watermark_excel_file(file: File) -> File:
        """
        Apply INTERNAL USE ONLY watermark on every page of Excel workbook file.

        Return new File object with same name and updated content.
        """
        watermark_location = finders.find("submission/internal-use-only-watermark.png")

        with file.open("rb") as file_handler:
            workbook: openpyxl.Workbook = openpyxl.load_workbook(file_handler)
        for worksheet in workbook.worksheets:
            img = openpyxl.drawing.image.Image(watermark_location)
            img.anchor = "A1"
            worksheet.add_image(img)

        with tempfile.TemporaryDirectory() as tempdir:
            temp_location = Path(tempdir) / "watermarked"
            workbook.save(temp_location)

            with open(temp_location, "rb") as file_handler:
                return File(BytesIO(file_handler.read()), file.name)


def detect_error(exc):
    """Detect specific validation error from general database error."""
    match = re.search(
        r"Key \(package_id, fastq_prefix\)=\(\d+, (.*)?\) already exists\.",
        str(exc),
        re.M,
    )
    if match:
        duplicated_fastq = match.groups()[0]
        return serializers.ValidationError(
            f'fastq_prefix: Duplicated value "{duplicated_fastq}".',
        )
    return exc
