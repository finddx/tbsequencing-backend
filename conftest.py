from datetime import datetime, date
from unittest.mock import patch

import botocore.session
import pytest
from botocore.stub import Stubber
from psycopg2.extras import DateRange
from rest_framework.test import APIClient

from biosql.models import Taxon
from genphen.models import Country, Drug, DrugSynonym, GrowthMedium, PDSAssessmentMethod
from identity.models import User
from submission.models import Sample
from submission.util.datagen import PackageGenerator


# pylint: disable=invalid-name,redefined-outer-name,unused-argument
class Helper:
    """General-purpose pytest helper."""

    def __init__(self, settings):
        """Populate helper object with app settings."""
        self.settings = settings

    @staticmethod
    def abs_uri(loc: str):
        """Build absolute URI for given location."""
        if loc.startswith("/"):
            loc = loc[1:]
        return f"http://testserver/{loc}"

    def ftime(self, datetime_obj: datetime):
        """Serialize datetime object using app-defined datetime format (DRF default)."""
        return datetime_obj.strftime(self.settings.REST_FRAMEWORK["DATETIME_FORMAT"])

    def ptime(self, datetime_str: str):
        """Deserialize datetime string using app-defined datetime format (DRF default)."""
        return datetime.strptime(
            datetime_str,
            self.settings.REST_FRAMEWORK["DATETIME_FORMAT"],
        )


@pytest.fixture
def util(settings):
    """General-purpose testing helper."""
    return Helper(settings)


@pytest.fixture
def api_client(db):  # pylint: disable=unused-argument,invalid-name
    """DRF API client."""
    return APIClient()


@pytest.fixture
def country_of(db):
    """Get or create country."""

    def _country(three: str, two: str = None, num: int = None, name: str = None):
        """Actual working function."""
        return Country.objects.get_or_create(
            three_letters_code=three,
            defaults={
                "two_letters_code": two or three[:2],
                "country_usual_name": name or three,
                "country_id": num or sum(ord(char) for char in three),
            },
        )[0]

    return _country


@pytest.fixture
def countries(db, country_of):
    """Generate series of countries."""
    return [
        country_of("ABW", name="Aruba", num=533),
        country_of("FRA", name="France", num=250),
        country_of("KAZ", name="Kazakhstan", num=398, two="KZ"),
        country_of("CHE", name="Switzerland", num=756),
    ]


@pytest.fixture
def assessment_methods(db):
    """Generate series of PDS assessment methods."""
    methods = []
    for method in (
        "Resistance Ratio",
        "Proportions",
        "Direct",
        "Nitrate reductase assay",
        "WHO",
    ):
        methods.append(
            PDSAssessmentMethod.objects.get_or_create(
                method_name=method,
            )[0],
        )
    return methods


@pytest.fixture
def growth_mediums(db):
    """Generate series of DST methods (growth mediums)."""
    mediums = []
    for medium in [
        "MGIT",
        "BACTEC460",
        "LJ",
        "Agar",
        "Middlebrook7H9",
        "Middlebrook7H10",
        "Middlebrook7H11",
        "Waynes",
        "Marks Biphasic",
        "MODS",
    ]:
        mediums.append(
            GrowthMedium.objects.get_or_create(medium_name=medium)[0],
        )
    return mediums


@pytest.fixture
def drug_of(db):  # pylint: disable=unused-argument,invalid-name
    """Create and return selected drug."""

    def _drug(code: str, name: str = None, synonyms: list = None):
        """Actual working function."""
        drug = Drug.objects.get_or_create(
            drug_code=code,
            defaults={
                "drug_name": name or code,
            },
        )[0]
        if not synonyms:
            synonyms = []
        synonyms.append(code)
        for syn in synonyms:
            DrugSynonym.objects.get_or_create(
                drug_name_synonym=syn,
                defaults={
                    "drug": drug,
                    "code": DrugSynonym.CodeType.THREE_LETTER,
                },
            )
        return drug

    return _drug


@pytest.fixture
def drugs(drug_of):
    """Create all drugs and 3-letter code drug synonyms."""
    return [
        drug_of("INH", "Isoniazid"),
        drug_of("RIF", "Rifampicin"),
        drug_of("STR", "Streptomycin", ["STM"]),
        drug_of("EMB", "Ethambutol"),
        drug_of("OFX", "Ofloxacin", ["OFL"]),
        drug_of("CAP", "Capreomycin"),
        drug_of("AMK", "Amikacin", ["AMI"]),
        drug_of("KAN", "Kanamycin"),
        drug_of("PZA", "Pyrazinamide"),
        drug_of("LFX", "Levofloxacin", ["LEV", "LEVO", "LVX"]),
        drug_of("MFX", "Moxifloxacin", ["MXF", "MOXI", "MOX"]),
        drug_of("CYC", "Cycloserine", ["DCS", "Cs"]),
        drug_of("ETO", "Ethionamide", ["ETH"]),
        drug_of("DLM", "Delamanid"),
        drug_of("BDQ", "Bedaquiline"),
        drug_of("LZD", "Linezolid"),
        drug_of("CFZ", "Clofazimine"),
        drug_of("PMD", "Pretomanid"),
        drug_of("PAS", "Para - Aminosalicylic Acid"),
        drug_of("PTO", "Prothionamide"),
        drug_of("AMX/CLV", "Amoxicillin-Clavulanate"),
        drug_of("MB", "Rifabutin", ["RFB"]),
        drug_of("IPM/CLN", "Imipenem - Cilastatin"),
        drug_of("CLR", "Clarithromycin"),
        drug_of("FT", "Fluoroquinolones"),
        drug_of("AG/CP", "Aminoglycosides"),
        drug_of("GFX", "Gatifloxacin"),
        drug_of("CIP", "Ciprofloxacin"),
        drug_of("SIT", "Sitafloxacin", ["STX"]),
        drug_of("AZT", "Azithromycin"),
    ]


def create_user(name, is_staff=False):
    """Generate a user, for using in test cases."""
    user_data = {
        "first_name": name.title(),
        "last_name": f"{name}son".title(),
        "username": name.lower(),
        "email": f"{name.lower()}@example.com",
        "password": name.lower() * 2,
    }
    user = User.objects.create_user(is_staff=is_staff, **user_data)
    return user


@pytest.fixture
def alice(db):  # pylint: disable=unused-argument,invalid-name
    """
    Test user named Alice.

    Registered, email verified.
    No admin rights.
    """
    return create_user("alice")


@pytest.fixture
def alice_package(alice):  # pylint: disable=redefined-outer-name
    """Alice package data generator."""
    return PackageGenerator(user=alice)


@pytest.fixture
def john(db):  # pylint: disable=unused-argument,invalid-name
    """
    Test random user named John.

    Registered, email verified.
    No admin rights.
    """
    return create_user("john")


@pytest.fixture
def mick(db):  # pylint: disable=unused-argument,invalid-name
    """
    Test random user named Mick.

    Registered, email verified.
    Profile is not verified.
    No admin rights.
    """
    return create_user("mick")


@pytest.fixture
def admin(db):  # pylint: disable=unused-argument,invalid-name
    """
    Test random user named Admin.

    Registered, email verified.
    With admin rights.
    """
    return create_user("admin", is_staff=True)


@pytest.fixture
def client_of(db):  # pylint: disable=unused-argument,invalid-name
    """Return API client of selected user."""

    def _client_of(user):
        """Actual working function."""
        client = APIClient()
        client.force_authenticate(user)
        return client

    return _client_of


@pytest.fixture
def password_of(db):  # pylint: disable=unused-argument,invalid-name
    """Return password of selected user."""

    def _password_of(user):
        """Actual working function."""
        return user.username * 2

    return _password_of


@pytest.fixture(autouse=True)
def fs_mock():
    """FS Storage mock, to avoid file persistence."""
    with patch("django.core.files.storage.FileSystemStorage.save") as mock:
        mock.return_value = "filename.ext"
        yield


@pytest.fixture
def s3_stub(mocker) -> Stubber:
    """S3 botocore client stub."""
    s3_client = botocore.session.get_session().create_client("s3")

    with Stubber(s3_client) as stub:
        mocker.patch(
            "submission.services.s3bucket.boto3.client",
            side_effect=lambda *args, **kwargs: stub.client,
        )

        yield stub


@pytest.fixture
def new_sample(db):  # pylint: disable=invalid-name,unused-argument
    """Create new sample record."""

    def _new_sample(yoi: int = None, country: str = None) -> Sample:
        """Actual function."""
        return Sample.objects.create(
            ncbi_taxon=Taxon.objects.first(),
            sampling_date=DateRange(date(yoi, 1, 1), date(yoi, 12, 31))
            if yoi
            else None,
            country=country,
        )

    return _new_sample
