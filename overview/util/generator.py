import random
from datetime import date
from itertools import cycle

from django.utils.crypto import get_random_string
from faker import Faker
from psycopg2.extras import DateRange

from biosql.models import Taxon
from genphen.models import (
    Country,
    Drug,
    PDSAssessmentMethod,
    FormattedAnnotationPerGene,
)
from identity.models import User
from submission.models import PDSTest, Sample, SampleAlias, Package, Genotype
from ..models import Gene


# TODO remove or rewrite
# pylint: disable=too-many-instance-attributes
class FakeGenerator:
    """Fake objects provider, used to generate fake data."""

    def __init__(self):
        """Cache data, required for object generation."""
        self.countries = Country.objects.all()
        self.drugs = Drug.objects.all()
        self.gene_ids = list(Gene.objects.values_list("gene_db_crossref", flat=True))
        self.faker = Faker()

        self.pds_method = PDSAssessmentMethod.objects.first()
        self.user = User.objects.filter(username="alice").first()
        self.package, _ = Package.objects.get_or_create(
            owner=self.user,
            name="MEGA package",
        )
        self.yois = list(range(1964, 2023))
        self.concentrations = (None, *(i / 100 for i in range(100)))
        self.test_result = None
        self.drug = None
        self.concentration = None
        self.pds_test_counter = 0
        self.taxon = Taxon.objects.first()
        self.aliases = []
        self.alias = None
        self.samples = []
        self.genotype_samples = []
        self.variants = []

    # def fake_global_drug(self):
    #     """Generate single GlobalDrug object."""
    #     while True:
    #         yield GlobalDrug(
    #             drug=random.choice(self.drugs),
    #             country_id=random.choice(self.countries),
    #             resistance_type=random.choice(GlobalDrug.Type.choices)[0],
    #             date=self.faker.date_between(start_date="-30y", end_date="now"),
    #             susceptible=random.randint(100, 2000),
    #             resistant=random.randint(100, 2000),
    #             intermediate=random.randint(100, 2000),
    #         )

    def fake_pds_test(self):
        """
        Generate single PDS test.

        1 to 10 tests with same test result generated for every sample.
        1% chance that same sample will have different result for same drug.
        """
        while True:
            if not self.aliases:
                # bulk pre-create 10000 samples,
                # so we don't need to issue sql for every sample
                self.samples = []
                for _ in range(1000):
                    yoi = random.choice(self.yois)
                    country = random.choice(self.countries)
                    sample = Sample(
                        ncbi_taxon=self.taxon,
                        country=country,
                        package=self.package,
                        sampling_date=DateRange(date(yoi, 1, 1), date(yoi, 12, 31))
                        if yoi
                        else None,
                    )
                    self.samples.append(sample)

                    self.aliases.append(
                        SampleAlias(
                            name=get_random_string(16),
                            sample=sample,
                            package=self.package,
                        ),
                    )
                Sample.objects.bulk_create(self.samples)
                SampleAlias.objects.bulk_create(self.aliases)

            self.test_result = random.choice("SRI")
            self.drug = random.choice(self.drugs)
            self.concentration = random.choice(self.concentrations)
            self.alias = self.aliases.pop()

            for _ in range(random.randint(1, 10)):
                if random.random() < 0.99:
                    result = self.test_result
                else:
                    # 1% chance for test result to differ
                    result = random.choice("SRI".replace(self.test_result, ""))

                yield PDSTest(
                    test_result=result,
                    drug=self.drug,
                    concentration=self.concentration,
                    method=self.pds_method,
                    package=self.package,
                    sample_id=self.alias.sample_id,
                    sample_alias=self.alias,
                    staging=False,
                )

    def fake_fapg(self):
        """Generate fake formatted_annotations_per_gene record."""
        existing_gene_variants = FormattedAnnotationPerGene.objects.distinct(
            "variant_id",
        ).values_list(
            "variant_id",
            flat=True,
        )

        self.variants = list(existing_gene_variants)

        existing_gene_ids = set(
            FormattedAnnotationPerGene.objects.distinct(
                "gene_db_crossref_id",
            ).values_list(
                "gene_db_crossref_id",
                flat=True,
            ),
        )

        # for every gene id that is not present in FakeFAPG table
        for gene_id in set(self.gene_ids).difference(existing_gene_ids):
            for i in range(random.randint(1, 10)):
                # every gene has its own variant set
                # 1-10 variants per gene
                variant_id = int(f"{gene_id}{i}")

                # this is for fake_genotype
                self.variants.append(variant_id)

                yield FormattedAnnotationPerGene(
                    variant_id=variant_id,
                    gene_db_crossref_id=gene_id,
                    predicted_effect=random.choice(
                        ["UPSTREAM", "SYNONYMOUS", "MISSENSE"],
                    ),
                    nucleotidic_annotation=get_random_string(4),
                    proteic_annotation=get_random_string(5),
                    distance_to_reference=random.randint(1, 1000),
                )

    def fake_genotype(self):
        """Generate fake genotype record."""
        # Arrange all samples between variants through genotypes,
        # so we have 1 genotype per sample, but many genotypes per variant.
        # Here genotype sets are exclusive for every variant
        busy_sample_ids = (
            Genotype.objects.values_list("sample_id", flat=True).distinct().order_by()
        )
        free_sample_ids = Sample.objects.exclude(pk__in=busy_sample_ids).values_list(
            "pk",
            flat=True,
        )
        for variant_id, sample in zip(cycle(self.variants), free_sample_ids):
            yield Genotype(
                sample_id=sample,
                variant_id=variant_id,
                genotyper=get_random_string(3),
                quality=random.random(),
                reference_ad=random.randint(1, 1000),
                alternative_ad=random.randint(1, 1000),
                total_dp=random.randint(1, 1000),
                genotype_value=get_random_string(6),
            )

    def data(self):
        """Return list of (model class, single object generator function) associations."""
        return [
            # TODO do we still need it?
            # (PDSTest, self.fake_pds_test),
            # (GlobalDrug, self.fake_global_drug),
            # (FormattedAnnotationPerGene, self.fake_fapg),
            # (Genotype, self.fake_genotype),
        ]
