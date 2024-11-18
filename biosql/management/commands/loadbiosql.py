import json
import logging
import os
from io import StringIO

import boto3
import psycopg2
from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection, transaction
from Bio import SeqIO, SeqUtils, Entrez
from BioSQL import BioSeqDatabase  # pylint: disable=no-name-in-module

log = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Recreate biosql schema and fill it with data from Entrez.

    Be careful using it outside migrations,
    recreating involves dropping all related tables from other schemas.
    """

    def add_arguments(self, parser):
        """Add arguments to the command."""
        parser.add_argument(
            "--aws_region",
            help="AWS Secret Manager region location",
            default=settings.AWS_DEFAULT_REGION,
        )
        parser.add_argument(
            "--nuccore_id",
            help="Genbank nucleotide db identification value",
            default="NC_000962.3",
        )
        parser.add_argument(
            "--secret_arn",
            help="AWS Secret Manager ARN for NCBI Entrez API key and email",
            default=settings.ENTREZ_SECRET_ARN,
        )

    def get_gbk(self, **options):
        """Obtain and parse gbk string."""
        session = boto3.session.Session()

        log.info("obtaining NCBI Entrez API email/key")
        secret = json.loads(
            session.client(
                service_name="secretsmanager",
                region_name=options["aws_region"],
            ).get_secret_value(SecretId=options["secret_arn"])["SecretString"],
        )

        Entrez.email = secret["email"]
        Entrez.api_key = secret["api_key"]

        # Download the reference genome from the NCBI, as a gbk format with all the annotation
        log.info("downloading reference genome from NCBI")
        gbk_string = Entrez.efetch(
            db="nuccore",
            id=options["nuccore_id"],
            rettype="gbwithparts",
            retmode="text",
        ).read()

        log.info("parsing gbk string")
        gbk = list(SeqIO.parse(StringIO(gbk_string), "genbank"))

        log.info("adding sequence to feature locations")
        for entry in gbk:
            for feature in entry.features:
                loc = feature.location
                if feature.type.endswith("RNA"):
                    if str(loc.strand) == "1":
                        feature.qualifiers["sequence"] = [
                            str(entry.seq[loc.start : loc.end]),
                        ]
                    elif str(loc.strand) == "-1":
                        feature.qualifiers["sequence"] = [
                            str(
                                entry.seq[loc.start : loc.end].reverse_complement(),
                            ),
                        ]
                elif feature.type == "CDS":
                    feature.qualifiers["sequence"] = [
                        SeqUtils.seq3(feature.qualifiers["translation"][0]),
                    ]

        return gbk

    def handle(self, *args, **options):
        """Handle the command."""
        # first download all data we need
        gbk = self.get_gbk(**options)

        with transaction.atomic():
            curr = connection.cursor()
            log.info("dropping biosql schema")
            curr.execute("DROP SCHEMA IF EXISTS biosql CASCADE")

            # create biosql schema
            biosqldb_path = os.path.join(
                apps.get_app_config("biosql").path,
                "sql",
                "biosqldb-pg.sql",
            )
            with open(biosqldb_path, encoding="utf-8") as file:
                log.info("creating biosql schema")
                curr.execute(file.read())

            # we need biosql schema to be transparent for NCBI scripts to work
            curr.execute("SET search_path TO biosql,public")

            server = BioSeqDatabase.DBServer(connection, psycopg2)

            try:
                database = server[gbk[0].id]
                database.adaptor.execute("DELETE FROM biosql.bioentry")
            except KeyError:
                database = server.new_database(gbk[0].id)

            # Load the annotation into biosqldb
            log.info("loading annotation into biosql")
            database.load(gbk)

            log.info("populating dbxref from seqfeature_qualifier_source")
            database.adaptor.execute(
                """
                INSERT INTO biosql.dbxref(dbname, accession, version)
                    SELECT
                        'Protein',
                        value,
                        0
                    FROM biosql.seqfeature_qualifier_value
                        INNER JOIN biosql.term ON term.term_id=seqfeature_qualifier_value.term_id
                        WHERE name='protein_id';
                """,
            )

            log.info("done!")
