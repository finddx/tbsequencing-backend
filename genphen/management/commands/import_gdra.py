import csv
import logging

from django.core.management.base import BaseCommand
from django.db import transaction

from genphen.models import Drug, GeneDrugResistanceAssociation
from overview.models import Gene, DrugGene

log = logging.getLogger(__name__)


class Command(BaseCommand):
    """Import gene-drug resistance association data from CSV file."""

    def add_arguments(self, parser):
        """Add arguments to the command."""
        parser.add_argument(
            "--file",
            help="Path to CSV file to be imported",
        )

    def handle(self, *args, **options):
        """Handle the command."""
        # first download all data we need

        drugs = {
            drug_name.lower(): drug_id
            for drug_name, drug_id in Drug.objects.values_list("drug_name", "drug_id")
        }

        # read and validate data
        data = []
        with open(options["file"], encoding="utf-8") as file:
            reader = csv.reader(file, delimiter=",")
            rows = list(reader)
            for tier, locus_tag, drug_name in rows[1:]:
                dbxref_id = Gene.objects.filter(locus_tag=locus_tag).values_list(
                    "gene_db_crossref",
                )[0][0]

                drug_id = drugs.get(drug_name.lower())
                if drug_id is None:
                    log.info(
                        "Association '%s - %s (tier %s)' not added, "
                        "no drug named %s.",
                        locus_tag,
                        drug_name,
                        tier,
                        drug_name,
                    )
                    continue

                data.append(
                    (
                        dbxref_id,
                        drug_id,
                        int(tier),
                    ),
                )

        # import data
        with transaction.atomic():
            # "truncate" table before
            GeneDrugResistanceAssociation.objects.all().delete()
            objs = []
            for dbxref_id, drug_id, tier in data:
                gdra = GeneDrugResistanceAssociation(
                    gene_db_crossref_id=dbxref_id,
                    drug_id=drug_id,
                    tier=tier,
                )
                objs.append(gdra)

            GeneDrugResistanceAssociation.objects.bulk_create(objs)

        log.info("imported %d from %d records", len(objs), len(rows[1:]))

        DrugGene.refresh()
        log.info("refreshed overview_druggene matview")
