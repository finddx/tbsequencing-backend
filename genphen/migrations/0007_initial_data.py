# Generated by Django 4.1.5 on 2023-05-22 10:16
import pycountry
from django.db import migrations
import logging
import os.path

log = logging.getLogger(__name__)


def fill_genphen_initial_data(apps, schema_editor):
    """Fill initial genphen data."""
    Country = apps.get_model("genphen", "Country")
    if Country.objects.exists():
        log.info("Country table is not empty, skipping initial data filling")
        return
    countries = []
    for country in list(pycountry.countries):
        countries.append(
            Country(
                three_letters_code=country.alpha_3,
                country_id=country.numeric,
                two_letters_code=country.alpha_2,
                country_usual_name=country.name,
                country_official_name=getattr(country, "official_name", ""),
            ),
        )

    Country.objects.bulk_create(countries)
    log.info("filled country table")

    sql_dir = os.path.join(os.path.dirname(__file__), "..", "sql")
    conn = schema_editor.connection

    with conn.cursor() as cursor:
        with open(os.path.join(sql_dir, "0007_initial_data.sql")) as file:
            cursor.execute(file.read())


class Migration(migrations.Migration):

    dependencies = [
        ("genphen", "0006_microdilutionplateconcentration_and_more"),
    ]

    operations = [
        migrations.RunPython(
            fill_genphen_initial_data,
            migrations.RunPython.noop,
        ),
    ]